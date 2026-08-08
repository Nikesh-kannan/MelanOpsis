import numpy as np

TAXONOMY_NAMES = {
    "nv": "Melanocytic Nevus (Benign Mole)",
    "mel": "Malignant Melanoma",
    "bcc": "Basal Cell Carcinoma",
    "bkl": "Benign Keratosis",
    "akiec": "Actinic Keratosis",
    "df": "Dermatofibroma",
    "vasc": "Vascular Lesion"
}

def compute_7class_subdiagnoses(calibrated_risk: float, color_var: float, feature_score: float) -> list[dict]:
    """
    Computes probabilistic sub-diagnoses across 7 clinical skin lesion taxonomy classes:
    - mel: Malignant Melanoma
    - nv: Melanocytic Nevus (Benign Mole)
    - bcc: Basal Cell Carcinoma
    - bkl: Benign Keratosis
    - akiec: Actinic Keratosis
    - df: Dermatofibroma
    - vasc: Vascular Lesion
    
    Returns: Sorted list of dicts: [{"class_code": "nv", "name": "Melanocytic Nevus", "probability": 0.88, "type": "benign"}]
    """
    r = float(calibrated_risk)
    
    # Base logits
    p_mel = r * 0.85
    p_bcc = r * 0.12 + (0.05 if color_var > 14.0 else 0.0)
    p_akiec = r * 0.03
    
    # Benign distribution
    p_nv = (1.0 - r) * 0.82 if color_var < 10.0 else (1.0 - r) * 0.60
    p_bkl = (1.0 - r) * 0.12 + (0.10 if color_var >= 10.0 and r < 0.35 else 0.0)
    p_df = (1.0 - r) * 0.04
    p_vasc = (1.0 - r) * 0.02
    
    # Raw vector
    scores = np.array([p_nv, p_mel, p_bcc, p_bkl, p_akiec, p_df, p_vasc], dtype=np.float32)
    scores = np.maximum(scores, 0.001)
    
    # Softmax normalization
    exp_scores = np.exp(scores - np.max(scores))
    probs = exp_scores / np.sum(exp_scores)
    
    class_order = ["nv", "mel", "bcc", "bkl", "akiec", "df", "vasc"]
    malignant_codes = {"mel", "bcc", "akiec"}
    
    results = []
    for code, prob in zip(class_order, probs):
        results.append({
            "class_code": code,
            "name": TAXONOMY_NAMES[code],
            "probability": round(float(prob), 4),
            "is_malignant": code in malignant_codes
        })
        
    results.sort(key=lambda item: item["probability"], reverse=True)
    return results
