import pytesseract
import cv2
import os
import numpy as np
from wand.image import Image

# Set the Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\loco2\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

def test_ocr(pdf_path, output_path):
    # Initialize variables to store the different text results
    ocr_results = []

    with Image(filename=pdf_path, resolution=300) as pdf:
        # Convert the PDF to images with 300 DPI resolution
        with pdf.convert('png') as images:
            for i, image in enumerate(images.sequence):
                with Image(image) as img:
                    # Convert the image to grayscale
                    gray_image = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)

                    # Threshold the image to remove noise
                    threshold_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

                    # Perform OCR using Tesseract
                    text = pytesseract.image_to_string(threshold_image, lang='eng')

                    # Append the result to the list
                    ocr_results.append(text)

                    # Write the text to a file
                    with open(os.path.join(output_path, f"result_{i+1}.txt"), 'w') as f:
                        f.write(text)


test_ocr('sample.pdf',r'C:\Users\loco2\OneDrive - EY\Documents\GitHub\PCubed')