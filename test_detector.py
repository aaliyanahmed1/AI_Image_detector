"""
Test script for the Gradient PCA Detector
Creates synthetic test data if real data is not available
"""

import numpy as np
from gradient_pca_detector import (
    GradientPCADetector,
    rgb_to_luminance,
    compute_gradients,
    flatten_gradients,
    compute_covariance,
    extract_features_from_image
)
from pathlib import Path
import cv2
import tempfile
import os


def create_test_image(size=(256, 256), noise_level=0.1, pattern='smooth'):
    """Create a synthetic test image."""
    img = np.zeros((*size, 3), dtype=np.uint8)
    
    if pattern == 'smooth':
        # Smooth gradient (simulating real image)
        for i in range(size[0]):
            for j in range(size[1]):
                img[i, j] = [
                    int(128 + 127 * np.sin(i / 20)),
                    int(128 + 127 * np.sin(j / 20)),
                    int(128 + 127 * np.sin((i+j) / 30))
                ]
    elif pattern == 'noisy':
        # High-frequency noise (simulating AI-generated)
        img = np.random.randint(0, 256, (*size, 3), dtype=np.uint8)
    
    # Add noise
    noise = np.random.normal(0, noise_level * 255, img.shape)
    img = np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    
    return img


def test_pipeline_components():
    """Test individual pipeline components."""
    print("Testing pipeline components...")
    
    # Create test RGB image
    test_img = create_test_image()
    
    # Test 1: RGB to Luminance
    L = rgb_to_luminance(test_img.astype(np.float32) / 255.0)
    assert L.shape == test_img.shape[:2], "Luminance shape mismatch"
    assert np.all(L >= 0) and np.all(L <= 1), "Luminance out of range"
    print("✓ RGB to Luminance: PASSED")
    
    # Test 2: Compute Gradients
    Gx, Gy = compute_gradients(L)
    assert Gx.shape == L.shape, "Gradient Gx shape mismatch"
    assert Gy.shape == L.shape, "Gradient Gy shape mismatch"
    print("✓ Compute Gradients: PASSED")
    
    # Test 3: Flatten Gradients
    M = flatten_gradients(Gx, Gy)
    expected_rows = L.shape[0] * L.shape[1]
    assert M.shape == (expected_rows, 2), f"Flatten shape mismatch: {M.shape}"
    print("✓ Flatten Gradients: PASSED")
    
    # Test 4: Compute Covariance
    C = compute_covariance(M)
    assert C.shape == (2, 2), f"Covariance shape mismatch: {C.shape}"
    assert np.allclose(C, C.T), "Covariance matrix not symmetric"
    print("✓ Compute Covariance: PASSED")
    
    print("\nAll component tests passed!\n")


def test_detector_with_synthetic_data():
    """Test detector with synthetic images."""
    print("Testing detector with synthetic data...")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        real_dir = Path(tmpdir) / "real"
        fake_dir = Path(tmpdir) / "fake"
        real_dir.mkdir()
        fake_dir.mkdir()
        
        # Create synthetic images
        print("Creating synthetic test images...")
        for i in range(5):
            # Real-like images (smooth patterns)
            real_img = create_test_image(pattern='smooth', noise_level=0.05)
            cv2.imwrite(str(real_dir / f"real_{i}.png"), 
                       cv2.cvtColor(real_img, cv2.COLOR_RGB2BGR))
            
            # Fake-like images (noisy patterns)
            fake_img = create_test_image(pattern='noisy', noise_level=0.2)
            cv2.imwrite(str(fake_dir / f"fake_{i}.png"),
                       cv2.cvtColor(fake_img, cv2.COLOR_RGB2BGR))
        
        # Initialize detector
        detector = GradientPCADetector(n_components=2, standardize=True)
        
        # Load images
        from gradient_pca_detector import load_images_from_directory
        real_images = load_images_from_directory(real_dir)
        fake_images = load_images_from_directory(fake_dir)
        
        print(f"Loaded {len(real_images)} real and {len(fake_images)} fake images")
        
        # Fit detector
        print("Fitting detector...")
        detector.fit(real_images, fake_images, verbose=True)
        
        # Test prediction
        print("\nTesting predictions...")
        result = detector.predict(real_images[0])
        print(f"Prediction on real image: {result['label']} (confidence: {result['confidence']:.3f})")
        
        result = detector.predict(fake_images[0])
        print(f"Prediction on fake image: {result['label']} (confidence: {result['confidence']:.3f})")
        
        # Test batch prediction
        print("\nTesting batch prediction...")
        results = detector.predict_batch(real_images + fake_images)
        print(f"Processed {len(results)} images")
        
        # Test PCA components
        components = detector.get_pca_components()
        variance = detector.get_explained_variance()
        print(f"\nPCA Components shape: {components.shape}")
        print(f"Explained variance: {variance}")
        
        print("\n✓ Detector tests passed!")


def test_feature_extraction():
    """Test feature extraction from saved image."""
    print("\nTesting feature extraction...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create and save test image
        test_img = create_test_image()
        img_path = Path(tmpdir) / "test.png"
        cv2.imwrite(str(img_path), cv2.cvtColor(test_img, cv2.COLOR_RGB2BGR))
        
        # Extract features
        features = extract_features_from_image(img_path)
        assert features.shape == (4,), f"Feature shape mismatch: {features.shape}"
        print(f"✓ Feature extraction: PASSED (shape: {features.shape})")


if __name__ == "__main__":
    print("=" * 60)
    print("Gradient PCA Detector Test Suite")
    print("=" * 60)
    
    try:
        test_pipeline_components()
        test_feature_extraction()
        test_detector_with_synthetic_data()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

