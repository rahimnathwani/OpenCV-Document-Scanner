from fasthtml.common import *
from pathlib import Path
import cv2
import os
from scan import DocScanner
from crop import crop_and_save
from extract_digits_2 import extract_digits
from pyimagesearch import transform

app, rt = fast_app()

# Create directories for uploads and results
upload_dir = Path("uploads")
results_dir = Path("results")
upload_dir.mkdir(exist_ok=True)
results_dir.mkdir(exist_ok=True)

def process_uploaded_image(input_path, output_dir):
    # Get base filename without extension
    basename = os.path.basename(input_path)
    name, ext = os.path.splitext(basename)
    
    # Step 1: Scan the document to get rectangular image
    scanner = DocScanner(interactive=False)
    scanned_path = output_dir / f"{name}_scanned{ext}"
    
    # Load and process the image
    image = cv2.imread(str(input_path))
    assert image is not None, f"Failed to load image: {input_path}"
    
    # Get the contour and transform
    ratio = image.shape[0] / 500.0
    rescaled_image = cv2.resize(image, (int(image.shape[1] / ratio), 500))
    screenCnt = scanner.get_contour(rescaled_image)
    warped = transform.four_point_transform(image, screenCnt * ratio)
    
    # Apply sharpening
    sharpen = cv2.GaussianBlur(warped, (0, 0), 3)
    sharpen = cv2.addWeighted(warped, 1.5, sharpen, -0.5, 0)
    cv2.imwrite(str(scanned_path), sharpen)
    
    # Step 2: Crop the region with digits
    crop_params = [(0.75, 0.14, 0.4, 0)]
    crop_and_save(str(scanned_path), crop_params, str(output_dir))
    
    # Step 3: Extract digits from the cropped region
    cropped_path = output_dir / f"{name}_scanned_crop_0{ext}"
    digits_dir = output_dir / 'digits'
    digits_dir.mkdir(exist_ok=True)
    
    # Extract digits with error handling
    try:
        extract_digits(str(cropped_path), str(digits_dir))
        digit_count = len([f for f in os.listdir(digits_dir) if f.endswith('.png')])
        print(f"Extracted {digit_count} digits")
    except Exception as e:
        print(f"Error during digit extraction: {str(e)}")
        raise
    
    # Verify digits were extracted
    digit_files = sorted([f for f in digits_dir.glob('*.png')])
    print(f"Found {len(digit_files)} digit files: {[f.name for f in digit_files]}")
    
    return {
        'original': f"uploads/{basename}",
        'scanned': f"results/{name}/{name}_scanned{ext}",
        'cropped': f"results/{name}/{name}_scanned_crop_0{ext}",
        'digits': [f"results/{name}/digits/{f.name}" for f in digit_files]
    }

@rt('/')
def get():
    return Titled("Document Scanner",
        Article(
            H1("Upload Document to Scan"),
            Form(hx_post=upload, hx_target="#results", enctype="multipart/form-data")(
                Input(type="file", name="file", accept="image/*"),
                Button("Upload & Process", type="submit", cls='primary'),
            ),
            Div(id="results")
        )
    )

def display_results(paths):
    return Article(
        H2("Processing Results"),
        Section(
            H3("Original Image"),
            Img(src=f"/{paths['original']}", style="max-width: 500px"),
            H3("Scanned Document"),
            Img(src=f"/{paths['scanned']}", style="max-width: 500px"),
            H3("Cropped ID Region"),
            Img(src=f"/{paths['cropped']}", style="max-width: 500px"),
            H3(f"Extracted Digits ({len(paths['digits'])} found)"),
            Div(style="display: flex; flex-wrap: wrap; gap: 10px")(
                *[Img(src=f"/{digit}", style="max-width: 50px") for digit in paths['digits']]
            ) if paths['digits'] else P("No digits were extracted")
        )
    )

@rt
async def upload(file: UploadFile):
    # Save uploaded file
    filename = file.filename
    file_path = upload_dir / filename
    
    # Create unique results directory for this upload
    name = os.path.splitext(filename)[0]
    output_dir = results_dir / name
    output_dir.mkdir(exist_ok=True)
    
    # Save the uploaded file
    content = await file.read()
    file_path.write_bytes(content)
    
    # Process the image
    try:
        result_paths = process_uploaded_image(file_path, output_dir)
        return display_results(result_paths)
    except Exception as e:
        return Article(
            H3("Error Processing Image", cls="error"),
            P(str(e))
        )

# Serve static files from uploads and results directories
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/results", StaticFiles(directory="results"), name="results")

serve() 