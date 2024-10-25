# Document Scanner

This project is a fork of [OpenCV-Document-Scanner](https://github.com/andrewdcampbell/OpenCV-Document-Scanner). It provides a set of tools to detect and crop ID cards from images, allowing further cropping to extract specific regions, such as dates.

## Requirements

- Python 3.x

## Installation

First, clone the repository:

```bash
git clone https://github.com/rahimnathwani/OpenCV-Document-Scanner.git
cd OpenCV-Document-Scanner
```

Install the required dependencies:
```
pip install -r requirements.txt
```
# Usage
## Basic Cropping
To crop an image to focus only on the ID card, run:
```
python scan.py --image image.jpg
```
Replace `image.jpg` with the name of your input image file. This command will create a cropped image in the output folder with the same filename.
# Further Cropping
You can further crop the output file by running:
```
python crop.py output/image.jpg
```
This command will generate a series of images in the output folder:
- `output/image_crop_0.jpg`
- `output/image_crop_1.jpg`
- `output/image_crop_2.jpg`
- `output/image_crop_3.jpg`
The final file, `output/image_crop_3.jpg`, will show only the Arabic date from the ID card.

# Customizing Cropping Parameters
If you need to extract other regions from the image, you can edit the `crop.py` file by modifying the `crop_params` list:
```
crop_params = [
    (0.1, 0.1, 0.1, 0.1),  # Remove 10% from each edge
    (0.2, 0.0, 0.0, 0.2),  # Remove 20% from top and right edges
    (0.0, 0.2, 0.2, 0.0),  # Remove 20% from bottom and left edges
    (0.8, 0.1, 0.4, 0.0),  # Extract just the date on the bottom right of the ID card
]
```
Adjust the values in the list to customize the cropping regions as needed.
