import sqlite3
import os
from wand.image import Image
import pytesseract
import sys
import cv2
import numpy as np
import time

# 30 seconds of proc time per files on average.

# Set up the OCR engine
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\loco2\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# specify path to the folder containing PDF files
pdf_folder_path = r"C:\Users\loco2\OneDrive - EY\Documents\GitHub\PCubed\test_pdf"

# create connection to SQLite database
conn = sqlite3.connect("pdf_text.db")

# create cursor object to execute SQL queries
cursor = conn.cursor()

# create table to store pdf file names and corresponding text
cursor.execute("CREATE TABLE IF NOT EXISTS pdf_text (file_name TEXT PRIMARY KEY, text_content TEXT)")

start_time = time.time()

# loop through all pdf files in folder
for pdf_file in os.listdir(pdf_folder_path):
    if pdf_file.endswith(".pdf"):
        pdf_path = os.path.join(pdf_folder_path, pdf_file)
        print(f"Processing file: {pdf_file}")
        
        # use Wand to convert each page of pdf to image
        with Image(filename=pdf_path) as img:
            for i, page_image in enumerate(img.sequence):
                # convert page image to grayscale numpy array
                page = cv2.cvtColor(np.array(page_image), cv2.COLOR_BGR2GRAY)
                
                # use pytesseract to extract text from image
                try:
                    text = pytesseract.image_to_string(page)
                except pytesseract.TesseractNotFoundError:
                    print("Tesseract not found, please install it and try again.")
                    sys.exit()
                
                # insert pdf file name and corresponding text into SQLite database
                cursor.execute("INSERT INTO pdf_text (file_name, text_content) VALUES (?, ?)",
                               (pdf_file + f"_page_{i+1}", text))
        conn.commit()

# close database connection
conn.close()

end_time = time.time()
print(f"Execution time: {end_time - start_time} seconds")

print("Done processing all PDF files.")
