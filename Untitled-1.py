""" import os
import sqlite3
from pdf2image import convert_from_path
import pytesseract
import cv2

# set up connection to database
conn = sqlite3.connect('pdf_text.db')
c = conn.cursor()

# create table to store data
c.execute('''CREATE TABLE IF NOT EXISTS pdf_data
             (filename text, page_number integer, text_content text)''')

# set up OCR engine
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# specify path to folder containing PDF files
pdf_folder_path = r'C:\Users\loco2\OneDrive - EY\Documents\GitHub\PCubed\test_pdf'

# loop over all PDF files in the folder
for filename in os.listdir(pdf_folder_path):
    if filename.endswith('.pdf'):
        pdf_path = os.path.join(pdf_folder_path, filename)
        pages = convert_from_path(pdf_path)
        page_number = 1
        # loop over all pages in the PDF file
        for page in pages:
            # convert page to grayscale
            page = cv2.cvtColor(np.array(page), cv2.COLOR_BGR2GRAY)
            # apply thresholding to enhance text
            _, thresh = cv2.threshold(page, 150, 255, cv2.THRESH_BINARY)
            # apply OCR to extract text
            text_content = pytesseract.image_to_string(thresh)
            # store data in database
            c.execute("INSERT INTO pdf_data VALUES (?, ?, ?)", (filename, page_number, text_content))
            page_number += 1

# commit changes to database and close connection
conn.commit()
conn.close()
"""