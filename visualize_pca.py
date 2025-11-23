"""
Visualization utility for PCA space and classification results
"""

import numpy as np
import matplotlib.pyplot as plt
from gradient_pca_detector import GradientPCADetector, load_images_from_directory
from pathlib import Path


def visualize_pca_space(detector: GradientPCADetector, 
                        real_images: list,
                        fake_images: list,
                        save_path: str = "pca_visualization.png"):
    """
    Visualize the PCA space with real and fake image projections.
    
    Args:
        detector: Fitted GradientPCADetector
        real_images: List of real image paths
        fake_images: List of fake image paths
        save_path: Path to save the visualization
    """
    if not detector.is_fitted:
        raise ValueError("Detector must be fitted before visualization")
    
    # Project all images
    real_projections = []
    fake_projections = []
    
    print("Projecting real images...")
    for img_path in real_images:
        try:
            proj = detector.project(img_path)
            real_projections.append(proj)
        except Exception as e:
            print(f"Warning: Failed to project {img_path}: {e}")
    
    print("Projecting fake images...")
    for img_path in fake_images:
        try:
            proj = detector.project(img_path)
            fake_projections.append(proj)
        except Exception as e:
            print(f"Warning: Failed to project {img_path}: {e}")
    
    if len(real_projections) == 0 or len(fake_projections) == 0:
        print("Not enough projections for visualization")
        return
    
    real_projections = np.array(real_projections)
    fake_projections = np.array(fake_projections)
    
    # Create visualization
    plt.figure(figsize=(12, 8))
    
    # Plot real images
    plt.scatter(real_projections[:, 0], real_projections[:, 1], 
               c='green', label='Real Images', alpha=0.6, s=50)
    
    # Plot fake images
    plt.scatter(fake_projections[:, 0], fake_projections[:, 1],
               c='red', label='AI Images', alpha=0.6, s=50)
    
    # Plot centroids
    if detector.real_centroid is not None:
        plt.scatter(detector.real_centroid[0], detector.real_centroid[1],
                   c='darkgreen', marker='*', s=300, label='Real Centroid',
                   edgecolors='black', linewidths=1)
    
    if detector.fake_centroid is not None:
        plt.scatter(detector.fake_centroid[0], detector.fake_centroid[1],
                   c='darkred', marker='*', s=300, label='AI Centroid',
                   edgecolors='black', linewidths=1)
    
    # Add decision boundary (line between centroids)
    if detector.real_centroid is not None and detector.fake_centroid is not None:
        mid_point = (detector.real_centroid + detector.fake_centroid) / 2
        direction = detector.fake_centroid - detector.real_centroid
        perp = np.array([-direction[1], direction[0]])
        perp = perp / np.linalg.norm(perp)
        
        # Extend line
        t = np.linspace(-10, 10, 100)
        line_points = mid_point + perp.reshape(-1, 1) * t
        
        plt.plot(line_points[0], line_points[1], 'k--', 
                alpha=0.5, linewidth=1, label='Decision Boundary')
    
    # Labels and title
    variance = detector.get_explained_variance()
    plt.xlabel(f'PC1 (Variance Explained: {variance[0]:.2%})')
    plt.ylabel(f'PC2 (Variance Explained: {variance[1]:.2%})')
    plt.title('PCA Space: Real vs AI-Generated Images')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Save
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"\nVisualization saved to: {save_path}")
    
    # Show
    plt.show()


def plot_prediction_confidence_distribution(detector: GradientPCADetector,
                                           real_images: list,
                                           fake_images: list,
                                           save_path: str = "confidence_distribution.png"):
    """
    Plot confidence score distribution for real and fake images.
    
    Args:
        detector: Fitted GradientPCADetector
        real_images: List of real image paths
        fake_images: List of fake image paths
        save_path: Path to save the plot
    """
    real_confidences = []
    fake_confidences = []
    
    print("Computing predictions for real images...")
    for img_path in real_images:
        try:
            result = detector.predict(img_path)
            if result['label'] == 'real':
                real_confidences.append(result['confidence'])
            else:
                real_confidences.append(1 - result['confidence'])
        except Exception as e:
            print(f"Warning: Failed to predict {img_path}: {e}")
    
    print("Computing predictions for fake images...")
    for img_path in fake_images:
        try:
            result = detector.predict(img_path)
            if result['label'] == 'ai':
                fake_confidences.append(result['confidence'])
            else:
                fake_confidences.append(1 - result['confidence'])
        except Exception as e:
            print(f"Warning: Failed to predict {img_path}: {e}")
    
    if len(real_confidences) == 0 or len(fake_confidences) == 0:
        print("Not enough predictions for visualization")
        return
    
    # Create histogram
    plt.figure(figsize=(10, 6))
    
    plt.hist(real_confidences, bins=20, alpha=0.7, label='Real Images', 
            color='green', edgecolor='black')
    plt.hist(fake_confidences, bins=20, alpha=0.7, label='AI Images',
            color='red', edgecolor='black')
    
    plt.xlabel('Confidence Score')
    plt.ylabel('Frequency')
    plt.title('Confidence Score Distribution')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"\nConfidence distribution saved to: {save_path}")
    plt.show()


if __name__ == "__main__":
    print("PCA Visualization Utility")
    print("=" * 50)
    print("\nTo use this utility:")
    print("1. Fit your detector first")
    print("2. Load your image paths")
    print("3. Call visualize_pca_space(detector, real_images, fake_images)")
    print("\nExample:")
    print("  from visualize_pca import visualize_pca_space")
    print("  visualize_pca_space(detector, real_images, fake_images)")

