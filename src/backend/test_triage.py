import sys
import os
import cv2
import numpy as np

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.models.inference import inference_service

def create_dermatoscopic_sample(is_cancer: bool) -> bytes:
    # 400x400 canvas with skin tone (warm beige/pinkish)
    img = np.ones((400, 400, 3), dtype=np.uint8)
    img[:, :, 0] = 170 # B
    img[:, :, 1] = 195 # G
    img[:, :, 2] = 225 # R
    
    # Add subtle skin texture noise
    noise = np.random.randint(-10, 10, (400, 400, 3), dtype=np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    if is_cancer:
        # Cancer / Melanoma: Irregular jagged border, multi-tone dark colors, asymmetrical
        center = (200, 200)
        # Jagged polygon
        pts = np.array([
            [120, 110], [210, 80], [280, 130], [290, 220],
            [230, 290], [150, 280], [100, 210], [90, 150]
        ], np.int32)
        
        # Dark brown / black base
        cv2.fillPoly(img, [pts], (25, 20, 35))
        
        # Inner dark black nodule
        pts_inner = np.array([[140, 130], [240, 110], [260, 200], [160, 230]], np.int32)
        cv2.fillPoly(img, [pts_inner], (10, 8, 15))
        
        # Red/blue vascular spots
        cv2.circle(img, (230, 180), 22, (30, 20, 160), -1) # Dark red
        cv2.circle(img, (150, 160), 18, (120, 40, 30), -1) # Dark blue/violet
    else:
        # Benign Mole / Nevus: Smooth circular, uniform medium brown
        cv2.circle(img, (200, 200), 65, (45, 65, 110), -1)
        cv2.circle(img, (200, 200), 55, (35, 55, 95), -1)
        
    _, buffer = cv2.imencode('.jpg', img)
    return buffer.tobytes()

if __name__ == "__main__":
    inference_service.load_model()
    
    mole_bytes = create_dermatoscopic_sample(is_cancer=False)
    cancer_bytes = create_dermatoscopic_sample(is_cancer=True)
    
    pred_mole = inference_service.predict(mole_bytes)
    pred_cancer = inference_service.predict(cancer_bytes)
    
    print("\n==========================================")
    print("      DERMSCANI TRIAGE TEST RESULTS       ")
    print("==========================================")
    print(f"BENIGN MOLE (Nevus):")
    print(f"  -> Decision:   {pred_mole['result'].upper()} ({'NO FLAG RAISED' if pred_mole['result'] == 'no_flag' else 'REFERRAL REQUIRED'})")
    print(f"  -> Confidence: {pred_mole['confidence']*100:.1f}%")
    print(f"  -> Risk Score: {pred_mole['risk_score']*100:.1f}%\n")
    
    print(f"HIGH-RISK CANCER (Melanoma):")
    print(f"  -> Decision:   {pred_cancer['result'].upper()} ({'REFERRAL REQUIRED' if pred_cancer['result'] == 'refer' else 'NO FLAG RAISED'})")
    print(f"  -> Confidence: {pred_cancer['confidence']*100:.1f}%")
    print(f"  -> Risk Score: {pred_cancer['risk_score']*100:.1f}%")
    print("==========================================\n")
