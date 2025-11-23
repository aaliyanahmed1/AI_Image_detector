"""
Example usage of the Gradient PCA Image Authenticity Detector
"""

from gradient_pca_detector import GradientPCADetector, load_images_from_directory
from pathlib import Path
import json


def main():
    # Initialize detector
    print("Initializing Gradient PCA Detector...")
    detector = GradientPCADetector(n_components=2, standardize=True)
    
    # Example 1: Load images from directories
    # Replace these paths with your actual image directories
    real_dir = Path("data/real_images")
    fake_dir = Path("data/fake_images")
    
    if real_dir.exists() and fake_dir.exists():
        print(f"\nLoading images from directories...")
        real_images = load_images_from_directory(real_dir)
        fake_images = load_images_from_directory(fake_dir)
        
        print(f"Found {len(real_images)} real images")
        print(f"Found {len(fake_images)} fake images")
        
        # Fit the detector
        print("\nFitting detector...")
        detector.fit(real_images, fake_images, verbose=True)
        
        # Example 2: Predict on a single image
        if len(real_images) > 0:
            print("\n" + "="*50)
            print("Example prediction on a real image:")
            result = detector.predict(real_images[0], method='centroid')
            print(json.dumps(result, indent=2))
        
        if len(fake_images) > 0:
            print("\n" + "="*50)
            print("Example prediction on a fake image:")
            result = detector.predict(fake_images[0], method='centroid')
            print(json.dumps(result, indent=2))
        
        # Example 3: Batch prediction
        print("\n" + "="*50)
        print("Batch prediction example:")
        test_images = real_images[:3] + fake_images[:3]
        results = detector.predict_batch(test_images)
        
        for img_path, result in zip(test_images, results):
            print(f"\n{img_path.name}:")
            print(f"  Label: {result['label']}")
            print(f"  Confidence: {result['confidence']:.3f}")
            print(f"  PCA Projection: {result['pca_projection']}")
    
    else:
        print("\n" + "="*50)
        print("Example directories not found. Here's how to use the detector:")
        print("\n1. Prepare your data:")
        print("   - Create directories: data/real_images/ and data/fake_images/")
        print("   - Add your training images to these directories")
        
        print("\n2. Load and fit:")
        print("   from gradient_pca_detector import GradientPCADetector, load_images_from_directory")
        print("   detector = GradientPCADetector(n_components=2)")
        print("   real_images = load_images_from_directory('data/real_images')")
        print("   fake_images = load_images_from_directory('data/fake_images')")
        print("   detector.fit(real_images, fake_images)")
        
        print("\n3. Predict on new images:")
        print("   result = detector.predict('path/to/image.jpg')")
        print("   print(f\"Label: {result['label']}, Confidence: {result['confidence']}\")")
        
        print("\n4. Get PCA statistics:")
        print("   variance = detector.get_explained_variance()")
        print("   print(f\"Explained variance: {variance}\")")


if __name__ == "__main__":
    main()

