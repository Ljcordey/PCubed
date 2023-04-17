import concurrent.futures
import multiprocessing
import os
import pathlib
import sqlite3
import sys
import time
from doctr.models import ocr
from doctr.models.text_recognition import transform
from wand.image import Image

# where we try using tensorflow and docTR
# specify path to the folder containing PDF files
pdf_folder_path = r"C:\Users\loco2\OneDrive - EY\Documents\GitHub\PCubed\test_pdf"

# create the database table if it does not exist
with sqlite3.connect("pdf_text.db") as conn:
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS pdf_text (file_name TEXT, page_number INTEGER, text_content TEXT)")

# function to process a single PDF file
def process_pdf(pdf_path):
    if pdf_path.suffix != ".pdf":
        return

    print(f"Processing file: {pdf_path.name}")

    # use Wand to convert each page of pdf to image
    with Image(filename=str(pdf_path)) as img:
        for i, page_image in enumerate(img.sequence):
            # use docTR to extract text from image
            page = transform(np.array(page_image))

            try:
                # use OCR engine to extract text from transformed image
                text = ocr(page)
            except Exception as e:
                print(f"Error extracting text from {pdf_path.name}, page {i+1}: {e}")
                continue

            # insert pdf file name, page number and corresponding text into SQLite database
            with sqlite3.connect("pdf_text.db") as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO pdf_text (file_name, page_number, text_content) VALUES (?, ?, ?)",
                                   (pdf_path.name, i+1, text))
                except sqlite3.Error as e:
                    print(f"Error inserting data for {pdf_path.name}, page {i+1}: {e}")
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
