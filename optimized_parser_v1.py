import concurrent.futures
import cv2
import multiprocessing
from multiprocessing import Pool
import numpy as np
import pathlib
import pytesseract
import sqlite3
import sys
import time
from wand.image import Image

# Set up the OCR engine
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\loco2\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# specify path to the folder containing PDF files
pdf_folder_path = r"C:\Users\loco2\OneDrive - EY\Documents\GitHub\PCubed\test_pdf"

# create the database table if it does not exist
with sqlite3.connect("pdf_text.db") as conn:
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS pdf_text (file_name TEXT, page_number INTEGER, text_content TEXT)")

# function to convert PDF page to image
def convert_page_to_image(pdf_path, page_number):
    with Image(filename=str(pdf_path), resolution=300) as img:
        page_image = img.sequence[page_number - 1]
        # convert page image to grayscale numpy array
        page = cv2.cvtColor(np.array(page_image), cv2.COLOR_BGR2GRAY)
        # Threshold the image to remove noise
        threshold_image = cv2.threshold(
            page, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
        )[1]
        return threshold_image


# function to process a single PDF file
def process_pdf(pdf_path):
    if pdf_path.suffix != ".pdf":
        return

    print(f"Processing file: {pdf_path.name}")

    # use Wand to convert each page of pdf to image
    with Image(filename=str(pdf_path), resolution=300) as img:
        for i, page_image in enumerate(img.sequence):
            # convert page image to grayscale numpy array
            page = cv2.cvtColor(np.array(page_image), cv2.COLOR_BGR2GRAY)
            # Threshold the image to remove noise
            threshold_image = cv2.threshold(page, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

            # use pytesseract to extract text from image
            try:
                text = pytesseract.image_to_string(threshold_image, lang='eng')
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

    print(f"Finished processing file: {pdf_path.name}")

if __name__ == '__main__':
    # start timing function
    start = time.time()

    # create a list of all PDF files in the folder
    pdf_files = [f for f in pathlib.Path(pdf_folder_path).iterdir() if f.suffix == '.pdf']

    # process the PDF files using multiprocessing
    with Pool(processes=4) as pool:
        pool.map(process_pdf, pdf_files)

    # end timing function
    end = time.time()
    print(f"Total processing time: {end - start} seconds")