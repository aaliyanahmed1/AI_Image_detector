"""
Baseline Image Authenticity Detector - No Training Required

This is a simplified detector that works immediately without training.
Uses statistical analysis of gradient patterns to distinguish real vs AI images.
"""

import numpy as np
from scipy.ndimage import sobel
import cv2
from pathlib import Path
from typing import Dict, Union
import warnings
warnings.filterwarnings('ignore')


def rgb_to_luminance(img: np.ndarray) -> np.ndarray:
    """Convert RGB to luminance using ITU-R BT.709 formula."""
    if img.ndim != 3 or img.shape[2] != 3:
        raise ValueError("Input must be RGB image with shape (H, W, 3)")
    return 0.2126 * img[..., 0] + 0.7152 * img[..., 1] + 0.0722 * img[..., 2]


def compute_gradients(L: np.ndarray) -> tuple:
    """Compute spatial gradients using Sobel operators."""
    Gx = sobel(L, axis=1)  # ∂L/∂x
    Gy = sobel(L, axis=0)  # ∂L/∂y
    return Gx, Gy


def extract_features(image_path: Union[str, Path]) -> Dict[str, float]:
    """
    Extract statistical features from image without requiring training.
    
    Returns features that can be used for classification based on known
    patterns in real vs AI-generated images.
    """
    # Load image
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    # Convert BGR to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_rgb = img_rgb.astype(np.float32) / 255.0
    
    # Step 1: RGB → Luminance
    L = rgb_to_luminance(img_rgb)
    
    # Step 2: Compute gradients
    Gx, Gy = compute_gradients(L)
    
    # Step 3: Extract statistical features
    # These features are based on known differences between real and AI images
    
    # Gradient magnitude
    gradient_magnitude = np.sqrt(Gx**2 + Gy**2)
    
    # Statistical features
    features = {
        # Variance in gradients (real images have more variation)
        'gradient_variance': float(np.var(gradient_magnitude)),
        
        # Mean gradient magnitude
        'gradient_mean': float(np.mean(gradient_magnitude)),
        
        # Gradient entropy (real images have higher entropy)
        'gradient_entropy': float(_compute_entropy(gradient_magnitude)),
        
        # High-frequency content (AI images often smoother)
        'high_freq_ratio': float(np.sum(gradient_magnitude > np.percentile(gradient_magnitude, 90)) / gradient_magnitude.size),
        
        # Gradient direction consistency
        'direction_consistency': float(_compute_direction_consistency(Gx, Gy)),
        
        # Luminance statistics
        'luminance_std': float(np.std(L)),
        'luminance_skew': float(_compute_skewness(L)),
        
        # Edge density
        'edge_density': float(np.sum(gradient_magnitude > 0.1) / gradient_magnitude.size),
    }
    
    return features


def _compute_entropy(data: np.ndarray) -> float:
    """Compute entropy of gradient distribution."""
    hist, _ = np.histogram(data.flatten(), bins=256, range=(0, 1))
    hist = hist[hist > 0]  # Remove zeros
    prob = hist / hist.sum()
    return -np.sum(prob * np.log2(prob))


def _compute_direction_consistency(Gx: np.ndarray, Gy: np.ndarray) -> float:
    """Compute consistency of gradient directions."""
    angles = np.arctan2(Gy, Gx)
    # Compute circular variance (lower = more consistent directions)
    mean_angle = np.angle(np.mean(np.exp(1j * angles)))
    variance = 1 - np.abs(np.mean(np.exp(1j * (angles - mean_angle))))
    return float(variance)


def _compute_skewness(data: np.ndarray) -> float:
    """Compute skewness of distribution."""
    mean = np.mean(data)
    std = np.std(data)
    if std == 0:
        return 0.0
    return float(np.mean(((data - mean) / std) ** 3))


def predict(image_path: Union[str, Path]) -> Dict:
    """
    Predict if image is real or AI-generated without training.
    
    Uses rule-based classification on statistical features.
    """
    try:
        features = extract_features(image_path)
        
        # Rule-based classification based on known patterns
        # These thresholds are based on empirical observations
        
        score = 0.0
        reasons = []
        
        # Real images typically have:
        # 1. Higher gradient variance (more texture variation)
        if features['gradient_variance'] > 0.01:
            score += 0.15
            reasons.append("High texture variation")
        else:
            score -= 0.1
            reasons.append("Low texture variation (AI-like)")
        
        # 2. Higher entropy (more randomness)
        if features['gradient_entropy'] > 5.0:
            score += 0.15
            reasons.append("High gradient entropy")
        else:
            score -= 0.1
            reasons.append("Low entropy (smoother, AI-like)")
        
        # 3. More high-frequency content
        if features['high_freq_ratio'] > 0.1:
            score += 0.15
            reasons.append("Rich high-frequency details")
        else:
            score -= 0.1
            reasons.append("Smooth gradients (AI-like)")
        
        # 4. Lower direction consistency (more varied edges)
        if features['direction_consistency'] > 0.3:
            score += 0.1
            reasons.append("Varied edge directions")
        else:
            score -= 0.15
            reasons.append("Consistent edge patterns (AI-like)")
        
        # 5. Higher luminance standard deviation
        if features['luminance_std'] > 0.15:
            score += 0.1
            reasons.append("Natural luminance variation")
        else:
            score -= 0.1
            reasons.append("Uniform luminance (AI-like)")
        
        # 6. Higher edge density
        if features['edge_density'] > 0.2:
            score += 0.1
            reasons.append("High edge density")
        else:
            score -= 0.1
            reasons.append("Low edge density (AI-like)")
        
        # Normalize score to [0, 1]
        score = (score + 1.0) / 2.0
        score = np.clip(score, 0.0, 1.0)
        
        # Determine label
        if score > 0.5:
            label = 'real'
            confidence = score
        else:
            label = 'ai'
            confidence = 1.0 - score
        
        return {
            'label': label,
            'confidence': float(confidence),
            'score': float(score),
            'features': features,
            'reasons': reasons[:3]  # Top 3 reasons
        }
        
    except Exception as e:
        raise ValueError(f"Prediction failed: {str(e)}")
