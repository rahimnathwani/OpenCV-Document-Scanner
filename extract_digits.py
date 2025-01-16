import cv2
import numpy as np
import os
from imutils import contours

def extract_digits(image_path, output_dir='digits'):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Read the image
    image = cv2.imread(image_path)
    assert image is not None, "Failed to load image"

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding to get binary image
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find contours
    contours_list, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Sort contours from left to right
    if contours_list:
        sorted_contours, _ = contours.sort_contours(contours_list, method="left-to-right")

        # Process each contour
        for i, contour in enumerate(sorted_contours):
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Extract the digit
            digit = thresh[y:y+h, x:x+w]
            
            # Create a square image with padding
            size = max(w, h) + 20  # Add some padding
            square = np.zeros((size, size), dtype=np.uint8)
            
            # Calculate position to paste the digit (center it)
            start_x = (size - w) // 2
            start_y = (size - h) // 2
            
            # Place the digit in the center of the square
            square[start_y:start_y+h, start_x:start_x+w] = digit
            
            # Save the digit
            output_path = os.path.join(output_dir, f"{i}.png")
            cv2.imwrite(output_path, square)
            print(f"Saved digit {i} to {output_path}")

if __name__ == "__main__":
    import argparse
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Extract digits from an image')
    parser.add_argument('image_path', help='Path to the input image')
    args = parser.parse_args()

    extract_digits(args.image_path)
