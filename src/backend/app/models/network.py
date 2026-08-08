import torch
import torch.nn as nn
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights

class DermScanNet(nn.Module):
    """
    EfficientNet-B0 based neural network fine-tuned for binary skin lesion triage:
    - High-Risk (1): Melanoma (mel), Basal Cell Carcinoma (bcc), Actinic Keratoses (akiec)
    - Low-Risk (0): Nevi (nv), Benign Keratosis (bkl), Dermatofibroma (df), Vascular (vasc)
    """
    def __init__(self, pretrained: bool = True):
        super(DermScanNet, self).__init__()
        
        weights = EfficientNet_B0_Weights.DEFAULT if pretrained else None
        self.backbone = efficientnet_b0(weights=weights)
        
        # Replace default classifier head
        in_features = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(p=0.3),
            nn.Linear(in_features, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(p=0.2),
            nn.Linear(128, 1) # Single logit output for binary classification
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        logits = self.backbone(x)
        return torch.sigmoid(logits)


def build_model(pretrained: bool = True) -> DermScanNet:
    model = DermScanNet(pretrained=pretrained)
    model.eval()
    return model
