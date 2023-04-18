import cv2
import os
import pytesseract
import sqlite3
import tempfile
from wand.api import library
from wand.image import Image
import concurrent.futures
import multiprocessing
import numpy as np
import pathlib
import sys
import time

# Set up the OCR engine
# Set up the OCR engine
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\loco2\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# Set the language and other OCR engine settings
config = '--psm 1 -l eng'

# specify path to the folder containing PDF files
pdf_folder_path = r"C:\Users\loco2\OneDrive - EY\Documents\GitHub\PCubed\test_pdf"

# create the database table if it does not exist
with sqlite3.connect("pdf_text.db") as conn:
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS pdf_text (file_name TEXT, page_number INTEGER, text_content TEXT)")

def process_pdf(pdf_path):
    """
    Extracts image from each page of a PDF file, applies image corrections and filters to improve the OCR accuracy,
    performs OCR on the images and extracts the text into a database.

    :param pdf_path: path to the PDF file to process
    """

    # create a temporary folder to hold the image data
    with tempfile.TemporaryDirectory() as temp_folder:
        # use Wand to convert each page of pdf to image
        with Image(filename=str(pdf_path)) as img:
            for i, page_image in enumerate(img.sequence):
                # convert SingleImage to proper Image object
                page_image = Image(page_image)

                # create a temporary file to hold the image data
                temp_image_path = os.path.join(temp_folder, f"page_{i+1}.jpg")
                # write the image data to the temporary file
                page_image.save(filename=temp_image_path)

                # read the image from the temporary file
                page = cv2.imread(temp_image_path)

                # apply image corrections and filters to improve OCR accuracy
                page = cv2.cvtColor(page, cv2.COLOR_BGR2GRAY)
                page = cv2.medianBlur(page, 3)
                page = cv2.threshold(page, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

                # use pytesseract to extract text from image
                try:
                    text = pytesseract.image_to_string(page, config=config)
                except pytesseract.TesseractNotFoundError:
                    print("Tesseract not found, please install it and try again.")
                    sys.exit()

                # insert pdf file name, page number and corresponding text into SQLite database
                with sqlite3.connect("pdf_text.db") as conn:
                    cursor = conn.cursor()
                    try:
                        cursor.execute("INSERT INTO pdf_text (file_name, page_number, text_content) VALUES (?, ?, ?)",
                                       (pdf_path.name, i+1, text))
                    except sqlite3.Error as e:
                        print(f"Error inserting data for {pdf_path.name}: {e}")
                    else:
                        # commit the changes to the database
                        conn.commit()


# start timing function
start = time.time()

# create a list of all PDF files in the folder
pdf_files = [f for f in pathlib.Path(pdf_folder_path).iterdir() if f.suffix == '.pdf']

# process the PDF files using multiprocessing
if __name__ == '__main__':
    multiprocessing.freeze_support()  # necessary for Windows platform
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(process_pdf, pdf_path) for pdf_path in pdf_files]

        # wait for all futures to complete

        # wait for all futures to complete
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
            except Exception as e:
                print(f"Error processing PDF file: {e}")

# end timing function
end = time.time()
print(f"Time taken: {end - start}")
