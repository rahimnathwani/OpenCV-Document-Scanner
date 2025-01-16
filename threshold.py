import cv2
import numpy as np
import os

# Parameters
BLUR_KERNEL_SIZE = 5  # Must be odd number. Larger = more blurring
THRESHOLD_VALUE = 64  # 0-255, pixels above this become white, below become black

def threshold_image(image_path):
    # Read the image
    image = cv2.imread(image_path)
    assert image is not None, "Failed to load image"

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (BLUR_KERNEL_SIZE, BLUR_KERNEL_SIZE), 0)
    
    # Apply binary thresholding
    _, thresh = cv2.threshold(blurred, THRESHOLD_VALUE, 255, cv2.THRESH_BINARY)
    
    # Generate output filename
    base_path, ext = os.path.splitext(image_path)
    output_path = f"{base_path}_bw{ext}"
    
    # Save the thresholded image
    cv2.imwrite(output_path, thresh)
    print(f"Saved thresholded image to {output_path}")

if __name__ == "__main__":
    import argparse
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Convert image to black and white using thresholding')
    parser.add_argument('image_path', help='Path to the input image')
    args = parser.parse_args()

    threshold_image(args.image_path) 