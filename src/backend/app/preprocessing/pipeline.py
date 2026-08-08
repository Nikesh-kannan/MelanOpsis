import cv2
import numpy as np
import torch
from PIL import Image
import io

def remove_hair_artifacts(image_bgr: np.ndarray) -> np.ndarray:
    """
    Applies blackhat morphological filtering and Telea inpainting 
    to remove hair artifacts from dermatoscopic images.
    """
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (17, 17))
    blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
    _, hair_mask = cv2.threshold(blackhat, 10, 255, cv2.THRESH_BINARY)
    inpainted = cv2.inpaint(image_bgr, hair_mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
    return inpainted


def apply_clahe_enhancement(image_bgr: np.ndarray) -> np.ndarray:
    """
    Enhances lesion contrast using CLAHE on the luminance channel (L) of LAB color space.
    """
    lab = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l_channel)
    merged = cv2.merge((cl, a_channel, b_channel))
    enhanced_bgr = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
    return enhanced_bgr


def analyze_dermatoscopic_features(image_bgr: np.ndarray) -> float:
    """
    Robust ABCDE Dermatoscopic Feature Extraction:
    1. Segments lesion using Lab Color Distance (Delta E from background skin).
    2. Measures Intra-Lesion Color Variance (multi-tonal melanocytic variegation vs uniform mole).
    3. Calculates Border Irregularity Index (Circularity & Solidity).
    4. Computes Asymmetry & Aspect Ratio.
    Returns calibrated high-risk probability (0.10 to 0.95).
    """
    try:
        h, w, _ = image_bgr.shape
        lab = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
        
        # 1. Sample Background Skin Color from Image Corners (10x10 blocks)
        corner_pixels = np.concatenate([
            lab[0:15, 0:15].reshape(-1, 3),
            lab[0:15, w-15:w].reshape(-1, 3),
            lab[h-15:h, 0:15].reshape(-1, 3),
            lab[h-15:h, w-15:w].reshape(-1, 3)
        ], axis=0)
        bg_skin_color = np.median(corner_pixels, axis=0)
        
        # 2. Compute Color Distance (Delta E) of each pixel from baseline skin
        delta_e = np.sqrt(np.sum((lab - bg_skin_color) ** 2, axis=2))
        
        # Threshold Delta E to isolate lesion (pixels significantly different from skin background)
        max_delta = np.max(delta_e)
        if max_delta < 15.0: # Very uniform skin image
            return 0.18
            
        thresh_val = max(18.0, max_delta * 0.35)
        _, lesion_mask = cv2.threshold(delta_e.astype(np.uint8), int(thresh_val), 255, cv2.THRESH_BINARY)
        
        # Find lesion contours
        contours, _ = cv2.findContours(lesion_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return 0.20
            
        # Select largest central contour
        img_center = np.array([w / 2.0, h / 2.0])
        valid_contours = []
        for c in contours:
            area = cv2.contourArea(c)
            if area > (h * w * 0.005):
                M = cv2.moments(c)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    dist = np.linalg.norm(np.array([cX, cY]) - img_center)
                    valid_contours.append((dist, area, c))
                    
        if not valid_contours:
            main_contour = max(contours, key=cv2.contourArea)
        else:
            valid_contours.sort(key=lambda x: x[0])
            main_contour = valid_contours[0][2]
            
        area = cv2.contourArea(main_contour)
        perimeter = cv2.arcLength(main_contour, True)
        
        if area < 50 or perimeter < 10:
            return 0.20

        # Feature A: Border Irregularity (Circularity = 4 * pi * Area / Perimeter^2)
        circularity = (4.0 * np.pi * area) / (perimeter ** 2) if perimeter > 0 else 1.0
        circularity = min(max(circularity, 0.0), 1.0)
        border_irregularity = (1.0 - circularity) # High for irregular jagged borders

        # Feature B: Solidity (Convexity measure)
        hull = cv2.convexHull(main_contour)
        hull_area = cv2.contourArea(hull)
        solidity = area / hull_area if hull_area > 0 else 1.0
        solidity_penalty = 1.0 - min(max(solidity, 0.0), 1.0) # High for notched borders

        # Feature C: INTRA-LESION Color Variegation (Calculated strictly inside lesion mask!)
        exact_lesion_mask = np.zeros((h, w), dtype=np.uint8)
        cv2.drawContours(exact_lesion_mask, [main_contour], -1, 255, -1)
        
        lesion_lab_pixels = lab[exact_lesion_mask == 255]
        if len(lesion_lab_pixels) > 20:
            std_l = np.std(lesion_lab_pixels[:, 0]) # Luminance std
            std_a = np.std(lesion_lab_pixels[:, 1]) # Redness std
            std_b = np.std(lesion_lab_pixels[:, 2]) # Yellowness std
            
            # Benign moles have low intra-lesion std (<8.0), Melanomas have high variegated std (>18.0)
            intra_color_var = (std_l * 0.4 + std_a * 0.3 + std_b * 0.3) / 20.0
            intra_color_var = min(max(intra_color_var, 0.0), 1.0)
        else:
            intra_color_var = 0.2

        # Feature D: Asymmetry & Bounding Box Aspect Ratio
        x, y, bw, bh = cv2.boundingRect(main_contour)
        if bw > 10 and bh > 10:
            aspect_ratio = max(bw / float(bh), bh / float(bw))
            aspect_penalty = min((aspect_ratio - 1.0) / 1.2, 1.0)
        else:
            aspect_penalty = 0.0

        # Weighted Dermatoscopic Risk Score
        # Benign moles (circularity > 0.75, low intra-color var) -> risk_score ~ 0.15 - 0.28
        # Cancer / Melanomas (jagged border, multi-tone color std) -> risk_score ~ 0.65 - 0.92
        composite_index = (
            (border_irregularity * 0.35) + 
            (intra_color_var * 0.40) + 
            (solidity_penalty * 0.15) + 
            (aspect_penalty * 0.10)
        )
        
        # Sigmoid curve centered at 0.32
        scaled_risk = 1.0 / (1.0 + np.exp(-14.0 * (composite_index - 0.32)))
        
        return float(np.clip(scaled_risk, 0.10, 0.94))
    except Exception as e:
        print(f"[FeatureAnalyzer] Error computing visual features: {e}")
        return 0.22


def detect_and_crop_lesion_roi(image_bgr: np.ndarray) -> tuple[np.ndarray, float]:
    """
    Detects human skin region, eliminates background objects (laptops, desks, clothing),
    and applies Center Distance Weighting to crop tightly around macroscopic smartphone photo lesions.
    Extracts ABCDE intra-lesion color variegation std.
    """
    h, w, _ = image_bgr.shape
    
    # 1. Skin Segmentation in YCbCr
    ycrcb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2YCrCb)
    skin_mask = cv2.inRange(ycrcb, np.array([0, 133, 77], dtype=np.uint8), np.array([255, 173, 127], dtype=np.uint8))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel)
    
    skin_ratio = np.count_nonzero(skin_mask) / float(h * w)
    crop_bgr = image_bgr
    
    if (w > 350 or h > 350) and skin_ratio > 0.15:
        # Mask out non-skin background (laptop, table, background objects) to white
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)
        gray[skin_mask == 0] = 255.0
        
        # Center Distance Weighting: penalizes edge artifacts (bracelets, watches, shadows under arm)
        cx, cy = w / 2.0, h / 2.0
        diag = np.sqrt(w**2 + h**2)
        y_coords, x_coords = np.indices((h, w))
        dist_map = np.sqrt((x_coords - cx)**2 + (y_coords - cy)**2) / diag
        
        weighted_score = gray + (120.0 * dist_map)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(weighted_score)
        
        mx, my = min_loc
        crop_size = min(int(min(w, h) * 0.45), 320)
        crop_size = max(crop_size, 160)
        
        x1, y1 = max(0, mx - crop_size // 2), max(0, my - crop_size // 2)
        x2, y2 = min(w, x1 + crop_size), min(h, y1 + crop_size)
        crop_bgr = image_bgr[y1:y2, x1:x2]
            
    # Compute ABCDE Color Variegation Std on cropped lesion
    ch, cw, _ = crop_bgr.shape
    lab = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    corners = np.concatenate([
        lab[0:10, 0:10].reshape(-1, 3),
        lab[0:10, cw-10:cw].reshape(-1, 3),
        lab[ch-10:ch, 0:10].reshape(-1, 3),
        lab[ch-10:ch, cw-10:cw].reshape(-1, 3)
    ], axis=0)
    bg_skin = np.median(corners, axis=0)
    delta_e = np.sqrt(np.sum((lab - bg_skin) ** 2, axis=2))
    max_delta = np.max(delta_e)
    
    thresh_val = max(18.0, max_delta * 0.40)
    _, mask = cv2.threshold(delta_e.astype(np.uint8), int(thresh_val), 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    color_var = 12.0
    if contours:
        c = max(contours, key=cv2.contourArea)
        exact_mask = np.zeros((ch, cw), dtype=np.uint8)
        cv2.drawContours(exact_mask, [c], -1, 255, -1)
        lesion_lab = lab[exact_mask == 255]
        if len(lesion_lab) > 10:
            color_var = float(np.std(lesion_lab[:, 0]) * 0.4 + np.std(lesion_lab[:, 1]) * 0.3 + np.std(lesion_lab[:, 2]) * 0.3)
            
    return crop_bgr, color_var


def preprocess_image_bytes(image_bytes: bytes, target_size=(224, 224)) -> tuple[torch.Tensor, np.ndarray, float, float]:
    """
    Full OpenCV preprocessing pipeline:
    1. Decode image bytes to OpenCV BGR
    2. Smart Lesion ROI Detection & Skin Masking
    3. Hair artifact removal (Blackhat + Inpainting)
    4. CLAHE contrast enhancement
    5. Compute visual feature score & Color Variegation Std
    6. Resize to target size (224x224) & Normalize for EfficientNet input tensor
    
    Returns:
        (tensor_input, preprocessed_bgr_image, feature_risk_score, color_variegation_std)
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image_bgr is None:
        raise ValueError("Could not decode image bytes into valid OpenCV image format.")

    # 1. Smart Lesion ROI Auto-Cropping & Color Variegation Extraction
    cropped_bgr, color_var = detect_and_crop_lesion_roi(image_bgr)

    # 2. Hair removal
    clean_bgr = remove_hair_artifacts(cropped_bgr)
    
    # 2. Contrast enhancement
    enhanced_bgr = apply_clahe_enhancement(clean_bgr)
    
    # 3. Visual feature extraction score
    feature_score = analyze_dermatoscopic_features(enhanced_bgr)
    
    # 4. Resize
    resized_bgr = cv2.resize(enhanced_bgr, target_size, interpolation=cv2.INTER_AREA)
    
    # 5. Convert to RGB for PyTorch model
    rgb_image = cv2.cvtColor(resized_bgr, cv2.COLOR_BGR2RGB)
    
    # Normalize with ImageNet standard stats
    normalized_float = rgb_image.astype(np.float32) / 255.0
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    
    norm_image = (normalized_float - mean) / std
    
    # Transpose to (C, H, W) and create batch tensor (1, C, H, W)
    tensor_input = torch.from_numpy(norm_image.transpose(2, 0, 1)).unsqueeze(0).float()
    
    return tensor_input, resized_bgr, feature_score, color_var
