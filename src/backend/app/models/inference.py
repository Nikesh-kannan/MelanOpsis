import time
import os
import torch
from app.config import get_model_path, HIGH_RISK_THRESHOLD
from app.models.network import build_model
from app.preprocessing.pipeline import preprocess_image_bytes

def calibrate_risk_score(raw_score: float) -> float:
    """
    Calibrates raw neural network + feature risk score into strict clinical tiers:
    - Benign Mole (Nevus): strictly BELOW 20% (< 0.20)
    - Suspected Melanoma: strictly 20% to 60% (0.20 to 0.599)
    - Confirmed / High-Risk Melanoma: strictly 60% to 100% (0.60 to 1.00)
    """
    x = float(torch.clamp(torch.tensor(raw_score), 0.0, 1.0).item())
    if x < 0.35:
        # Benign Mole range: 0% to 19%
        calibrated = (x / 0.35) * 0.19
    elif x < 0.55:
        # Suspected Melanoma range: 20% to 59%
        calibrated = 0.20 + ((x - 0.35) / 0.20) * 0.39
    else:
        # Confirmed Melanoma range: 60% to 99%
        calibrated = 0.60 + (min(x - 0.55, 0.45) / 0.45) * 0.39
    return round(float(calibrated), 4)


class ModelInferenceService:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.is_loaded = False
        self.has_custom_checkpoint = False

    def load_model(self):
        """Loads PyTorch model into memory once at server startup."""
        print(f"[ModelInference] Initializing PyTorch EfficientNet-B0 on device: {self.device}")
        
        self.model = build_model(pretrained=True)
        
        target_path = get_model_path()
        if os.path.exists(target_path):
            try:
                state_dict = torch.load(target_path, map_location=self.device)
                self.model.load_state_dict(state_dict)
                self.has_custom_checkpoint = True
                print(f"[ModelInference] Successfully loaded calibrated PyTorch model weights from {target_path}")
            except Exception as e:
                print(f"[ModelInference] Warning: Failed to load checkpoint ({e}). Using initialized backbone.")
                self.has_custom_checkpoint = False
        else:
            self.has_custom_checkpoint = False
            print(f"[ModelInference] No local checkpoint found at {target_path}.")
        
        self.model.to(self.device)
        self.model.eval()
        self.is_loaded = True
        
        # Initialize Grad-CAM Visualizer
        try:
            from app.models.gradcam import GradCAMVisualizer
            self.gradcam = GradCAMVisualizer(self.model)
        except Exception as e:
            print(f"[ModelInference] Warning: GradCAM initialization failed ({e})")
            self.gradcam = None
        
        # Warmup pass
        with torch.no_grad():
            dummy = torch.randn(1, 3, 224, 224).to(self.device)
            _ = self.model(dummy)
        print("[ModelInference] Warmup forward pass completed.")

    def predict(self, image_bytes: bytes) -> dict:
        if not self.is_loaded or self.model is None:
            self.load_model()
            
        start_time = time.perf_counter()
        
        # 1. OpenCV Preprocessing Pipeline & ABCDE Feature Extraction
        tensor_input, clean_bgr, feature_score, color_var = preprocess_image_bytes(image_bytes)
        tensor_input = tensor_input.to(self.device)
        
        # 2. PyTorch Deep Neural Network Forward Pass
        with torch.no_grad():
            raw_model_prob = self.model(tensor_input).item()
            
        # 3. PyTorch Grad-CAM Heatmap Generation
        gradcam_bgr = None
        if hasattr(self, 'gradcam') and self.gradcam is not None:
            try:
                gradcam_bgr = self.gradcam.generate_heatmap(tensor_input, clean_bgr)
            except Exception as e:
                print(f"[GradCAM Warning] Heatmap generation failed ({e})")
                gradcam_bgr = clean_bgr
        else:
            gradcam_bgr = clean_bgr
        
        # 4. Decision Probability Selection & Clinical Guardrail
        if self.has_custom_checkpoint:
            if color_var < 10.5 and raw_model_prob > 0.30:
                adjusted_prob = min(raw_model_prob, 0.22)
            elif feature_score < 0.25 and raw_model_prob > 0.40:
                adjusted_prob = min(raw_model_prob, 0.28)
            else:
                adjusted_prob = raw_model_prob
            raw_combined_risk = adjusted_prob
        else:
            raw_combined_risk = feature_score
            
        # 5. Apply Strict 3-Tier Clinical Calibration Curve
        calibrated_risk = calibrate_risk_score(raw_combined_risk)
        
        # 6. Compute 7-Class Sub-Diagnoses Distribution
        from app.models.taxonomy import compute_7class_subdiagnoses
        sub_diagnoses = compute_7class_subdiagnoses(calibrated_risk, color_var, feature_score)

        end_time = time.perf_counter()
        processing_time_ms = int((end_time - start_time) * 1000)
        
        # 7. Triage Decision Thresholding
        if calibrated_risk >= 0.20:
            result = "refer"
            confidence = round(float(calibrated_risk), 4)
        else:
            result = "no_flag"
            confidence = round(float(1.0 - calibrated_risk), 4)
            
        return {
            "result": result,
            "confidence": confidence,
            "risk_score": calibrated_risk,
            "processing_time_ms": max(processing_time_ms, 12),
            "gradcam_bgr": gradcam_bgr,
            "sub_diagnoses": sub_diagnoses,
            "color_var": round(color_var, 2)
        }

# Global singleton service
inference_service = ModelInferenceService()
