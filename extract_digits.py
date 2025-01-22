import cv2
import numpy as np
import os
from imutils import contours

# Thresholding parameters
BLUR_KERNEL_SIZE = 3  # Must be odd number. Larger = more blurring
THRESHOLD_VALUE = 64  # 0-255, pixels above this become white, below become black
INVERT = False # Whether to invert the output images
ORIGINAL = False  # Whether to use original image for digit extraction

def extract_digits(image_path, output_dir='digits'):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get the basename of the original file without extension
    base_name = os.path.splitext(os.path.basename(image_path))[0]

    # Read the image
    image = cv2.imread(image_path)
    assert image is not None, "Failed to load image"

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (BLUR_KERNEL_SIZE, BLUR_KERNEL_SIZE), 0)
    
    # Apply binary thresholding
    _, thresh = cv2.threshold(blurred, THRESHOLD_VALUE, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours_list, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours from left to right
    if contours_list:
        sorted_contours, _ = contours.sort_contours(contours_list, method="left-to-right")

        # Process each contour
        for i, contour in enumerate(sorted_contours):
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Make the bounding box square by expanding the smaller dimension
            size = max(w, h)
            # Calculate how much to expand width or height
            w_diff = size - w
            h_diff = size - h
            # Adjust x and y to keep digit centered while expanding to square
            x = max(0, x - w_diff // 2)
            y = max(0, y - h_diff // 2)
            # Ensure we don't go beyond image bounds
            size = min(size, image.shape[1] - x, image.shape[0] - y)
            
            # Extract the square digit region from either original or thresholded image
            if ORIGINAL:
                digit = image[y:y+size, x:x+size]
            else:
                digit = thresh[y:y+size, x:x+size]
                # Convert back to BGR for consistency if using thresholded image
                digit = cv2.cvtColor(digit, cv2.COLOR_GRAY2BGR)
            
            # Invert the image if INVERT is True
            if INVERT and not ORIGINAL:  # Only invert if not using original image
                digit = cv2.bitwise_not(digit)
            
            # Save the digit
            output_path = os.path.join(output_dir, f"{base_name}_{i}.png")
            cv2.imwrite(output_path, digit)
            print(f"Saved digit {i} to {output_path}")

if __name__ == "__main__":
    import argparse
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Extract digits from an image')
    parser.add_argument('image_path', help='Path to the input image')
    args = parser.parse_args()

    extract_digits(args.image_path)
