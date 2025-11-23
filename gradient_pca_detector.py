"""
Luminance-Gradient PCA Image Authenticity Detector

This module implements a PCA-based detector that analyzes image gradients
to distinguish between real and AI-generated images. The pipeline follows:
RGB → Luminance → Gradients → Flatten → Covariance → PCA → Classification
"""

import numpy as np
from scipy.ndimage import sobel
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import pairwise_distances
import cv2
from pathlib import Path
from typing import List, Tuple, Dict, Union, Optional
import warnings
warnings.filterwarnings('ignore')


def rgb_to_luminance(img: np.ndarray) -> np.ndarray:
    """
    Convert RGB image to luminance using ITU-R BT.709 formula.
    
    Args:
        img: Input image array of shape (H, W, 3) with RGB channels
        
    Returns:
        Luminance array of shape (H, W)
    """
    if img.ndim != 3 or img.shape[2] != 3:
        raise ValueError("Input must be RGB image with shape (H, W, 3)")
    
    # ITU-R BT.709 luminance weights
    return 0.2126 * img[..., 0] + 0.7152 * img[..., 1] + 0.0722 * img[..., 2]


def compute_gradients(L: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute spatial gradients using Sobel operators.
    
    Args:
        L: Luminance image of shape (H, W)
        
    Returns:
        Tuple of (Gx, Gy) gradient arrays, each of shape (H, W)
    """
    # Sobel operator: axis=1 for horizontal (x), axis=0 for vertical (y)
    Gx = sobel(L, axis=1)  # ∂L/∂x
    Gy = sobel(L, axis=0)  # ∂L/∂y
    return Gx, Gy


def flatten_gradients(Gx: np.ndarray, Gy: np.ndarray) -> np.ndarray:
    """
    Flatten gradient arrays into a 2D matrix M ∈ R^(N×2).
    
    Each row represents one pixel's gradient vector [Gx, Gy].
    
    Args:
        Gx: Horizontal gradients, shape (H, W)
        Gy: Vertical gradients, shape (H, W)
        
    Returns:
        Matrix M of shape (N, 2) where N = H * W
    """
    return np.stack([Gx.flatten(), Gy.flatten()], axis=1)


def compute_covariance(M: np.ndarray) -> np.ndarray:
    """
    Compute covariance matrix C = (1/N) M^T M.
    
    Args:
        M: Gradient matrix of shape (N, 2)
        
    Returns:
        Covariance matrix of shape (2, 2)
    """
    N = M.shape[0]
    if N == 0:
        raise ValueError("Empty gradient matrix")
    return (M.T @ M) / N


def extract_features_from_image(image_path: Union[str, Path]) -> np.ndarray:
    """
    Extract gradient features from a single image.
    
    Pipeline: RGB → Luminance → Gradients → Flatten → Covariance
    
    Args:
        image_path: Path to image file
        
    Returns:
        Feature vector (flattened covariance matrix or PCA projection)
    """
    # Load image
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    # Convert BGR to RGB (OpenCV uses BGR)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Convert to float32 for better precision
    img_rgb = img_rgb.astype(np.float32) / 255.0
    
    # Step 1: RGB → Luminance
    L = rgb_to_luminance(img_rgb)
    
    # Step 2: Compute gradients
    Gx, Gy = compute_gradients(L)
    
    # Step 3: Flatten into matrix M
    M = flatten_gradients(Gx, Gy)
    
    # Step 4: Compute covariance matrix
    C = compute_covariance(M)
    
    # Return flattened covariance matrix as feature vector
    # This captures the gradient statistics
    return C.flatten()


class GradientPCADetector:
    """
    PCA-based detector for image authenticity using luminance gradients.
    
    This class implements the complete pipeline:
    1. Extract gradient features from images
    2. Fit PCA on real and fake image features
    3. Project new images into PCA space
    4. Classify based on distance to real/fake clusters
    """
    
    def __init__(self, n_components: int = 2, standardize: bool = True):
        """
        Initialize the detector.
        
        Args:
            n_components: Number of PCA components to use
            standardize: Whether to standardize features before PCA
        """
        self.n_components = n_components
        self.standardize = standardize
        self.pca = PCA(n_components=n_components)
        self.scaler = StandardScaler() if standardize else None
        self.real_centroid = None
        self.fake_centroid = None
        self.real_features = None
        self.fake_features = None
        self.is_fitted = False
    
    def _extract_batch_features(self, image_paths: List[Union[str, Path]]) -> np.ndarray:
        """
        Extract features from a batch of images (memory-efficient).
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            Feature matrix of shape (n_images, feature_dim)
        """
        features = []
        for img_path in image_paths:
            try:
                feat = extract_features_from_image(img_path)
                features.append(feat)
            except Exception as e:
                print(f"Warning: Failed to process {img_path}: {e}")
                continue
        
        if len(features) == 0:
            raise ValueError("No valid images found")
        
        return np.array(features)
    
    def fit(self, 
            real_images: List[Union[str, Path]], 
            fake_images: List[Union[str, Path]],
            verbose: bool = True):
        """
        Fit the detector on real and fake images.
        
        Args:
            real_images: List of paths to real images
            fake_images: List of paths to fake/AI-generated images
            verbose: Whether to print progress
        """
        if verbose:
            print(f"Extracting features from {len(real_images)} real images...")
        
        # Extract features from real images
        real_feats = self._extract_batch_features(real_images)
        
        if verbose:
            print(f"Extracting features from {len(fake_images)} fake images...")
        
        # Extract features from fake images
        fake_feats = self._extract_batch_features(fake_images)
        
        # Combine all features
        all_features = np.vstack([real_feats, fake_feats])
        
        # Standardize if requested
        if self.standardize:
            all_features = self.scaler.fit_transform(all_features)
        
        # Fit PCA
        if verbose:
            print(f"Fitting PCA with {self.n_components} components...")
        
        pca_features = self.pca.fit_transform(all_features)
        
        # Split back into real and fake
        n_real = len(real_feats)
        real_pca = pca_features[:n_real]
        fake_pca = pca_features[n_real:]
        
        # Compute centroids for classification
        self.real_centroid = np.mean(real_pca, axis=0)
        self.fake_centroid = np.mean(fake_pca, axis=0)
        
        # Store features for distance computation
        self.real_features = real_pca
        self.fake_features = fake_pca
        
        self.is_fitted = True
        
        if verbose:
            print(f"Fitting complete. Real centroid: {self.real_centroid}, "
                  f"Fake centroid: {self.fake_centroid}")
    
    def project(self, image_path: Union[str, Path]) -> np.ndarray:
        """
        Project a single image into PCA space.
        
        Args:
            image_path: Path to image file
            
        Returns:
            PCA projection coordinates as array of shape (n_components,)
        """
        if not self.is_fitted:
            raise ValueError("Detector must be fitted before projection")
        
        # Extract features
        features = extract_features_from_image(image_path)
        features = features.reshape(1, -1)
        
        # Standardize if needed
        if self.standardize:
            features = self.scaler.transform(features)
        
        # Project to PCA space
        pca_projection = self.pca.transform(features)
        
        return pca_projection[0]
    
    def predict(self, 
                image_path: Union[str, Path],
                method: str = 'centroid') -> Dict:
        """
        Predict whether an image is real or AI-generated.
        
        Args:
            image_path: Path to image file
            method: Classification method ('centroid' or 'nearest_neighbor')
            
        Returns:
            Dictionary with prediction results:
            {
                'label': 'real' or 'ai',
                'confidence': float in [0, 1],
                'pca_projection': [x, y] coordinates,
                'stats': additional statistics
            }
        """
        if not self.is_fitted:
            raise ValueError("Detector must be fitted before prediction")
        
        # Project image to PCA space
        pca_proj = self.project(image_path)
        
        # Compute distances to real and fake clusters
        if method == 'centroid':
            dist_real = np.linalg.norm(pca_proj - self.real_centroid)
            dist_fake = np.linalg.norm(pca_proj - self.fake_centroid)
        elif method == 'nearest_neighbor':
            # Distance to nearest real/fake sample
            dist_real = np.min(pairwise_distances(
                pca_proj.reshape(1, -1), self.real_features
            ))
            dist_fake = np.min(pairwise_distances(
                pca_proj.reshape(1, -1), self.fake_features
            ))
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Classify based on distance
        total_dist = dist_real + dist_fake
        if total_dist == 0:
            confidence = 0.5
            label = 'real'  # Default
        else:
            # Confidence based on relative distance
            confidence_real = 1 - (dist_real / total_dist)
            confidence_fake = 1 - (dist_fake / total_dist)
            
            if confidence_real > confidence_fake:
                label = 'real'
                confidence = confidence_real
            else:
                label = 'ai'
                confidence = confidence_fake
        
        # Additional statistics
        stats = {
            'distance_to_real': float(dist_real),
            'distance_to_fake': float(dist_fake),
            'method': method,
            'pca_variance_explained': float(np.sum(self.pca.explained_variance_ratio_))
        }
        
        return {
            'label': label,
            'confidence': float(confidence),
            'pca_projection': pca_proj.tolist(),
            'stats': stats
        }
    
    def predict_batch(self, 
                     image_paths: List[Union[str, Path]],
                     method: str = 'centroid') -> List[Dict]:
        """
        Predict for multiple images.
        
        Args:
            image_paths: List of image file paths
            method: Classification method
            
        Returns:
            List of prediction dictionaries
        """
        return [self.predict(img_path, method=method) for img_path in image_paths]
    
    def get_pca_components(self) -> np.ndarray:
        """Get PCA components matrix."""
        if not self.is_fitted:
            raise ValueError("Detector must be fitted first")
        return self.pca.components_
    
    def get_explained_variance(self) -> np.ndarray:
        """Get explained variance ratio for each component."""
        if not self.is_fitted:
            raise ValueError("Detector must be fitted first")
        return self.pca.explained_variance_ratio_


def load_images_from_directory(directory: Union[str, Path], 
                               extensions: Tuple[str, ...] = ('.jpg', '.jpeg', '.png', '.bmp')) -> List[Path]:
    """
    Load all image paths from a directory.
    
    Args:
        directory: Directory path
        extensions: Allowed image file extensions
        
    Returns:
        List of image file paths
    """
    directory = Path(directory)
    if not directory.exists():
        raise ValueError(f"Directory does not exist: {directory}")
    
    image_paths = []
    for ext in extensions:
        image_paths.extend(directory.glob(f'*{ext}'))
        image_paths.extend(directory.glob(f'*{ext.upper()}'))
    
    return sorted(image_paths)


if __name__ == "__main__":
    # Example usage
    print("Gradient PCA Image Authenticity Detector")
    print("=" * 50)
    
    # Example: Initialize detector
    detector = GradientPCADetector(n_components=2, standardize=True)
    
    print("\nTo use this detector:")
    print("1. Prepare directories with real and fake images")
    print("2. Load image paths:")
    print("   real_images = load_images_from_directory('path/to/real')")
    print("   fake_images = load_images_from_directory('path/to/fake')")
    print("3. Fit the detector:")
    print("   detector.fit(real_images, fake_images)")
    print("4. Predict on new images:")
    print("   result = detector.predict('path/to/image.jpg')")
    print("   print(result)")

