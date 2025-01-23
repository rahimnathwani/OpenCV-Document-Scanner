import cv2
import numpy as np
import os
from imutils import contours

# Thresholding parameters
BLUR_KERNEL_SIZE = 3  
THRESHOLD_VALUE = 64
INVERT = False
ORIGINAL = False
EXPECTED_DIGITS = 15  # Number of digits we expect to find

def extract_digits(image_path, output_dir='digits'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"\nExtracting digits from {image_path}")
    print(f"Output directory: {output_dir}")

    base_name = os.path.splitext(os.path.basename(image_path))[0]
    image = cv2.imread(image_path)
    assert image is not None, "Failed to load image"
    
    print(f"Image size: {image.shape}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (BLUR_KERNEL_SIZE, BLUR_KERNEL_SIZE), 0)
    _, thresh = cv2.threshold(blurred, THRESHOLD_VALUE, 255, cv2.THRESH_BINARY_INV)

    # Save debug images
    debug_dir = os.path.join(output_dir, 'debug')
    os.makedirs(debug_dir, exist_ok=True)
    cv2.imwrite(os.path.join(debug_dir, 'gray.png'), gray)
    cv2.imwrite(os.path.join(debug_dir, 'thresh.png'), thresh)

    # Find contours
    contours_list, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"Found {len(contours_list)} initial contours")

    # Filter contours based on size and aspect ratio
    filtered_contours = []
    min_area = (image.shape[0] * image.shape[1]) / 1000  # Reduced from 100
    max_area = (image.shape[0] * image.shape[1]) / 8    # Increased from 10
    
    for contour in contours_list:
        x, y, w, h = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)
        aspect_ratio = float(w) / h if h != 0 else 0
        
        # Print debug info for larger contours
        if area > min_area / 2:
            print(f"Contour - Area: {area:.0f}, Aspect: {aspect_ratio:.2f}, Size: {w}x{h}")
        
        # Filter conditions:
        # 1. Minimum area to eliminate noise
        # 2. Maximum area to eliminate large artifacts
        # 3. Aspect ratio should be reasonable for digits (not too wide or tall)
        if (area > min_area and
            area < max_area and
            0.1 < aspect_ratio < 4.0):  # Relaxed from 0.2-3.0
            filtered_contours.append(contour)

    print(f"Found {len(filtered_contours)} contours after filtering")

    # Sort remaining contours left-to-right
    if filtered_contours:
        sorted_contours, _ = contours.sort_contours(filtered_contours, method="left-to-right")
        
        # Take only the expected number of digits
        sorted_contours = sorted_contours[:EXPECTED_DIGITS]
        print(f"Processing {len(sorted_contours)} contours")

        # Draw debug image with contours
        debug_image = image.copy()
        for i, contour in enumerate(sorted_contours):
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(debug_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(debug_image, str(i), (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        cv2.imwrite(os.path.join(debug_dir, 'contours.png'), debug_image)

        # Process each contour
        for i, contour in enumerate(sorted_contours):
            x, y, w, h = cv2.boundingRect(contour)
            
            # Make bounding box square
            size = max(w, h)
            w_diff = size - w
            h_diff = size - h
            x = max(0, x - w_diff // 2)
            y = max(0, y - h_diff // 2)
            size = min(size, image.shape[1] - x, image.shape[0] - y)
            
            if ORIGINAL:
                digit = image[y:y+size, x:x+size]
            else:
                digit = thresh[y:y+size, x:x+size]
                digit = cv2.cvtColor(digit, cv2.COLOR_GRAY2BGR)
            
            if INVERT and not ORIGINAL:
                digit = cv2.bitwise_not(digit)
            
            output_path = os.path.join(output_dir, f"{base_name}_{i}.png")
            cv2.imwrite(output_path, digit)
            print(f"Saved digit {i} to {output_path}")
    else:
        print("No valid contours found after filtering!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Extract digits from an image')
    parser.add_argument('image_path', help='Path to the input image')
    args = parser.parse_args()

    extract_digits(args.image_path)