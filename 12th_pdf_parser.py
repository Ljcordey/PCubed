import concurrent.futures
import cv2
import multiprocessing
import numpy as np
import pathlib
import pytesseract
import sqlite3
import sys
import time
from wand.image import Image as WandImage
from wand.color import Color

# Set up the OCR engine
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\loco2\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# specify path to the folder containing PDF files
pdf_folder_path = r"C:\Users\loco2\OneDrive - EY\Documents\GitHub\PCubed\test_pdf2"

# create the database table if it does not exist
with sqlite3.connect("pdf_text.db") as conn:
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS pdf_text (file_name TEXT, page_number INTEGER, text_content TEXT)")

# function to process a single PDF file
def process_pdf(pdf_path):
    if pdf_path.suffix != ".pdf":
        return

    print(f"Processing file: {pdf_path.name}")

    # use wand to convert each page of pdf to image
    with WandImage(filename=str(pdf_path), resolution=300) as pdf:
        for i, page in enumerate(pdf.sequence):
            with WandImage(page) as img:
                # convert page to grayscale numpy array
                img.background_color = Color('white')
                img.alpha_channel = 'remove'
                img.format = 'jpeg'
                page_array = np.asarray(bytearray(img.make_blob()), dtype=np.uint8)
                page_gray = cv2.imdecode(page_array, cv2.IMREAD_GRAYSCALE)

                # Threshold the image to remove noise
                threshold_image = cv2.threshold(page_gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

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
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
            except Exception as e:
                print(f"Error processing PDF file: {e}")

# end timing function
end = time.time()
print(f"Time taken: {end - start}")