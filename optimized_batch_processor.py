"""
Memory-efficient batch processor for large-scale image analysis
"""

import numpy as np
from pathlib import Path
from typing import List, Union, Iterator
from gradient_pca_detector import GradientPCADetector, extract_features_from_image
import multiprocessing as mp
from functools import partial


def process_image_batch(image_paths: List[Path], 
                       batch_size: int = 32) -> Iterator[np.ndarray]:
    """
    Process images in batches to save memory.
    
    Args:
        image_paths: List of image paths
        batch_size: Number of images to process at once
        
    Yields:
        Batch of feature vectors
    """
    for i in range(0, len(image_paths), batch_size):
        batch = image_paths[i:i + batch_size]
        features = []
        
        for img_path in batch:
            try:
                feat = extract_features_from_image(img_path)
                features.append(feat)
            except Exception as e:
                print(f"Warning: Failed to process {img_path}: {e}")
                continue
        
        if features:
            yield np.array(features)


def extract_features_parallel(image_paths: List[Path], 
                              n_workers: int = None) -> np.ndarray:
    """
    Extract features from images using parallel processing.
    
    Args:
        image_paths: List of image paths
        n_workers: Number of parallel workers (default: CPU count)
        
    Returns:
        Feature matrix
    """
    if n_workers is None:
        n_workers = min(mp.cpu_count(), 8)  # Limit to 8 workers
    
    def extract_single(path):
        try:
            return extract_features_from_image(path)
        except Exception as e:
            print(f"Error processing {path}: {e}")
            return None
    
    print(f"Processing {len(image_paths)} images with {n_workers} workers...")
    
    with mp.Pool(n_workers) as pool:
        features = pool.map(extract_single, image_paths)
    
    # Filter out None values
    features = [f for f in features if f is not None]
    
    if len(features) == 0:
        raise ValueError("No valid features extracted")
    
    return np.array(features)


class OptimizedGradientPCADetector(GradientPCADetector):
    """
    Memory-optimized version of GradientPCADetector with batch processing.
    """
    
    def fit_optimized(self,
                     real_images: List[Union[str, Path]],
                     fake_images: List[Union[str, Path]],
                     batch_size: int = 32,
                     use_parallel: bool = True,
                     n_workers: int = None,
                     verbose: bool = True):
        """
        Fit detector with memory-efficient batch processing.
        
        Args:
            real_images: List of paths to real images
            fake_images: List of paths to fake images
            batch_size: Batch size for processing
            use_parallel: Whether to use parallel processing
            n_workers: Number of parallel workers
            verbose: Whether to print progress
        """
        if use_parallel:
            # Parallel processing
            if verbose:
                print(f"Extracting features from {len(real_images)} real images (parallel)...")
            real_feats = extract_features_parallel(real_images, n_workers)
            
            if verbose:
                print(f"Extracting features from {len(fake_images)} fake images (parallel)...")
            fake_feats = extract_features_parallel(fake_images, n_workers)
        else:
            # Batch processing
            if verbose:
                print(f"Extracting features from {len(real_images)} real images (batched)...")
            real_feats = []
            for batch in process_image_batch(real_images, batch_size):
                real_feats.append(batch)
            real_feats = np.vstack(real_feats) if real_feats else np.array([])
            
            if verbose:
                print(f"Extracting features from {len(fake_images)} fake images (batched)...")
            fake_feats = []
            for batch in process_image_batch(fake_images, batch_size):
                fake_feats.append(batch)
            fake_feats = np.vstack(fake_feats) if fake_feats else np.array([])
        
        if len(real_feats) == 0 or len(fake_feats) == 0:
            raise ValueError("Need at least one valid real and fake image")
        
        # Combine features
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
        
        # Compute centroids
        self.real_centroid = np.mean(real_pca, axis=0)
        self.fake_centroid = np.mean(fake_pca, axis=0)
        
        # Store features
        self.real_features = real_pca
        self.fake_features = fake_pca
        
        self.is_fitted = True
        
        if verbose:
            print(f"Fitting complete. Real centroid: {self.real_centroid}, "
                  f"Fake centroid: {self.fake_centroid}")


if __name__ == "__main__":
    print("Optimized Batch Processor")
    print("=" * 50)
    print("\nThis module provides memory-efficient batch processing")
    print("for large-scale image analysis.")
    print("\nUsage:")
    print("  detector = OptimizedGradientPCADetector()")
    print("  detector.fit_optimized(real_images, fake_images,")
    print("                         use_parallel=True)")

