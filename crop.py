import cv2
import os

def crop_and_save(image_path, crop_params_list, output_dir='output'):
    # Load the image
    image = cv2.imread(image_path)
    assert image is not None, "Failed to load image"

    height, width = image.shape[:2]

    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Iterate through the crop parameters and process each cropped section
    for idx, (top, bottom, left, right) in enumerate(crop_params_list):
        # Calculate the pixel values based on the proportions
        top_px = int(top * height)
        bottom_px = int(height - (bottom * height))
        left_px = int(left * width)
        right_px = int(width - (right * width))

        # Crop the image
        cropped_image = image[top_px:bottom_px, left_px:right_px]

        # Save the cropped image
        basename = os.path.basename(image_path)
        name, ext = os.path.splitext(basename)
        output_path = os.path.join(output_dir, f"{name}_crop_{idx}{ext}")
        cv2.imwrite(output_path, cropped_image)
        print(f"Saved cropped image: {output_path}")

# Example usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python crop.py <image_path>")
        sys.exit(1)
        
    image_path = sys.argv[1]
    
    crop_params = [
        (0.1, 0.1, 0.1, 0.1),  # Remove 10% from each edge
        (0.2, 0.0, 0.0, 0.2),  # Remove 20% from top and right edges
        (0.0, 0.2, 0.2, 0.0),  # Remove 20% from bottom and left edges
        (0.8, 0.1, 0.4, 0.0), # Extract just the date on the bottom right of the ID card
    ]

    crop_and_save(image_path, crop_params)

