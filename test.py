import os
import cv2
from scan import DocScanner
from crop import crop_and_save
from extract_digits_2 import extract_digits

def process_image(input_path, output_base_dir='test_output'):
    # Get base filename without extension
    basename = os.path.basename(input_path)
    name, ext = os.path.splitext(basename)
    
    # Create output directory for this image
    output_dir = os.path.join(output_base_dir, name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Step 1: Scan the document to get rectangular image
    scanner = DocScanner(interactive=False)
    scanned_path = os.path.join(output_dir, f"{name}_scanned{ext}")
    
    # Load and process the image
    image = cv2.imread(input_path)
    assert image is not None, f"Failed to load image: {input_path}"
    
    # Get the contour and transform
    ratio = image.shape[0] / 500.0  # Same as in scan.py
    rescaled_image = cv2.resize(image, (int(image.shape[1] / ratio), 500))
    screenCnt = scanner.get_contour(rescaled_image)
    warped = transform.four_point_transform(image, screenCnt * ratio)
    
    # Apply sharpening as in scan.py
    sharpen = cv2.GaussianBlur(warped, (0, 0), 3)
    sharpen = cv2.addWeighted(warped, 1.5, sharpen, -0.5, 0)
    cv2.imwrite(scanned_path, sharpen)
    
    # Step 2: Crop the region with digits
    crop_params = [(0.75, 0.14, 0.4, 0)]  # Only the digits region
    crop_and_save(scanned_path, crop_params, output_dir)
    
    # Step 3: Extract digits from the cropped region
    cropped_path = os.path.join(output_dir, f"{name}_scanned_crop_0{ext}")
    digits_dir = os.path.join(output_dir, 'digits')
    extract_digits(cropped_path, digits_dir)
    
    # Count extracted digits
    digit_count = len([f for f in os.listdir(digits_dir) if f.endswith('.png')])
    return digit_count

def main():
    input_dir = 'test_input'
    output_dir = 'test_output'
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Process all images in input directory
    valid_formats = ['.jpg', '.jpeg', '.jp2', '.png', '.bmp', '.tiff', '.tif']
    results = []
    
    for filename in os.listdir(input_dir):
        ext = os.path.splitext(filename)[1].lower()
        if ext in valid_formats:
            input_path = os.path.join(input_dir, filename)
            try:
                digit_count = process_image(input_path)
                results.append((filename, digit_count))
                print(f"Successfully processed {filename} - found {digit_count} digits")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
    
    # Print summary
    print("\nProcessing Summary:")
    print("-" * 50)
    for filename, count in results:
        print(f"{filename}: {count} digits extracted")

if __name__ == "__main__":
    from pyimagesearch import transform  # Import here to avoid circular imports
    main() 