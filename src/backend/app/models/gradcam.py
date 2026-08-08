import cv2
import torch
import torch.nn.functional as F
import numpy as np

class GradCAMVisualizer:
    def __init__(self, model):
        self.model = model
        self.gradients = None
        self.activations = None
        
        # Target the last feature extraction layer in EfficientNet-B0 backbone
        target_layer = self.model.backbone.features[-1]
        target_layer.register_forward_hook(self._save_activation)
        target_layer.register_full_backward_hook(self._save_gradient)

    def _save_activation(self, module, input, output):
        self.activations = output

    def _save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0]

    def generate_heatmap(self, tensor_input: torch.Tensor, original_bgr: np.ndarray) -> np.ndarray:
        """
        Generates PyTorch Grad-CAM attention heatmap overlaid on original BGR image.
        Returns: Grad-CAM BGR image array
        """
        self.model.eval()
        tensor_input = tensor_input.clone().detach().requires_grad_(True)
        
        # Forward pass
        output = self.model(tensor_input)
        
        # Zero gradients
        self.model.zero_grad()
        
        # Backward pass on logit output
        output.backward(torch.ones_like(output))
        
        if self.gradients is None or self.activations is None:
            # Fallback overlay if hooks didn't trigger
            return original_bgr
            
        gradients = self.gradients.detach()
        activations = self.activations.detach()
        
        # Channel-wise mean pooling of gradients
        weights = torch.mean(gradients, dim=(2, 3), keepdim=True)
        
        # Weighted combination of forward activation maps
        cam = torch.sum(weights * activations, dim=1, keepdim=True)
        cam = F.relu(cam) # Apply ReLU to keep positive activations
        
        # Normalize heatmap to [0.0, 1.0]
        cam = cam.squeeze().cpu().numpy()
        if np.max(cam) != np.min(cam):
            cam = (cam - np.min(cam)) / (np.max(cam) - np.min(cam))
        else:
            cam = np.zeros_like(cam)
            
        # Resize heatmap to match original image dimensions
        h, w, _ = original_bgr.shape
        cam_resized = cv2.resize(cam, (w, h), interpolation=cv2.INTER_CUBIC)
        
        # Convert to 8-bit heatmap with JET colormap (Red/Yellow = High Risk, Blue = Low)
        heatmap_8u = np.uint8(255 * cam_resized)
        heatmap_colored = cv2.applyColorMap(heatmap_8u, cv2.COLORMAP_JET)
        
        # Blend Heatmap (45%) with original BGR image (55%)
        blended = cv2.addWeighted(heatmap_colored, 0.45, original_bgr, 0.55, 0)
        return blended
