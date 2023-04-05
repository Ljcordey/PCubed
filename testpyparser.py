import os
import re
import sqlite3
import PyPDF2
import pytesseract

# Set up the OCR engine
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Change the path to the Tesseract OCR executable to match your system

# Set up the database connection
conn = sqlite3.connect('pdf_database.db')
c = conn.cursor()

# Create the table to store the PDF data
c.execute('CREATE TABLE IF NOT EXISTS pdf_data (id INTEGER PRIMARY KEY, file_name TEXT, text_data TEXT)')

# Set up the directory path to the PDF files
pdf_directory = 'C:/pdf_files/'

# Loop through the PDF files in the directory
for file_name in os.listdir(pdf_directory):
    if file_name.endswith('.pdf'):
        # Open the PDF file and extract the text data
        with open(pdf_directory + file_name, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfFileReader(pdf_file)
            text_data = ''
            for page_num in range(pdf_reader.numPages):
                page = pdf_reader.getPage(page_num)
                text_data += page.extractText()
                
            # Clean up the text data
            text_data = re.sub(r'\n', ' ', text_data)  # Replace line breaks with spaces
            text_data = re.sub(r'\s+', ' ', text_data)  # Replace multiple spaces with single spaces
            
            # Insert the PDF data into the database
            c.execute('INSERT INTO pdf_data (file_name, text_data) VALUES (?, ?)', (file_name, text_data))
            conn.commit()

# Close the database connection
conn.close()
