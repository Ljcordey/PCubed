import concurrent.futures
import multiprocessing
import os
import pathlib
import queue
import shutil
import sqlite3
import sys
import tempfile
import time
from typing import List

import cv2
import numpy as np
import pytesseract
from wand.color import Color
from wand.image import Image as WandImage

# Set up the OCR engine
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Users\loco2\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
)


# specify path to the folder containing PDF files
pdf_folder_path = r"C:\Users\loco2\OneDrive - EY\Documents\GitHub\PCubed\test_pdf2"


# create the database table if it does not exist
with sqlite3.connect("pdf_text.db") as conn:
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS pdf_text (file_name TEXT, page_number INTEGER, text_content TEXT)"
    )


def process_pdf(
    pdf_path: pathlib.Path, output_queue: multiprocessing.Queue, temp_dir: str
):
    if pdf_path.suffix != ".pdf":
        return

    print(f"Processing file: {pdf_path.name}")

    # use wand to convert each page of pdf to image
    with WandImage(filename=str(pdf_path), resolution=300) as pdf:
        for i, page in enumerate(pdf.sequence):
            with WandImage(page) as img:
                # convert page to grayscale numpy array
                img.background_color = Color("white")
                img.alpha_channel = "remove"
                img.format = "jpeg"
                page_array = np.asarray(bytearray(img.make_blob()), dtype=np.uint8)
                page_gray = cv2.imdecode(page_array, cv2.IMREAD_GRAYSCALE)

                # Threshold the image to remove noise
                threshold_image = cv2.threshold(
                    page_gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
                )[1]

                # use pytesseract to extract text from image
                try:
                    text = pytesseract.image_to_string(threshold_image, lang="eng")
                except pytesseract.TesseractNotFoundError:
                    print("Tesseract not found, please install it and try again.")
                    sys.exit()

                # insert pdf file name, page number and corresponding text into SQLite database
                try:
                    with sqlite3.connect("pdf_text.db") as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO pdf_text (file_name, page_number, text_content) VALUES (?, ?, ?)",
                            (pdf_path.name, i + 1, text),
                        )
                        # commit the changes to the database
                        conn.commit()
                except sqlite3.Error as e:
                    print(f"Error inserting data for {pdf_path.name}: {e}")

    # move the processed PDF to temporary directory for cleanup later
    shutil.move(str(pdf_path), os.path.join(temp_dir, pdf_path.name))

    print(f"Finished processing file: {pdf_path.name}")
    output_queue.put(pdf_path.name)


# start timing function
import contextlib
start = time.time()

# create a list of all PDF files in the folder
pdf_files = [f for f in pathlib.Path(pdf_folder_path).iterdir() if f.suffix == ".pdf"]

# process the PDF files using multiprocessing
if __name__ == "__main__":
    multiprocessing.freeze_support()  # necessary for Windows platform
    with (concurrent.futures.ThreadPoolExecutor(
            max_workers=os.cpu_count()
        ) as executor, tempfile.TemporaryDirectory() as temp_dir):
        output_queue = multiprocessing.Manager().Queue()
        futures = []
        for pdf_path in pdf_files:
            future = executor.submit(process_pdf, pdf_path, output_queue, temp_dir)
            futures.append(future)

            # wait for all futures to complete
            completed_files = set()
            errors = []
            while len(completed_files) < len(pdf_files):
                for future in concurrent.futures.as_completed(futures):
                    with contextlib.suppress(queue.Empty):
                        completed_file = output_queue.get(timeout=1)
                        completed_files.add(completed_file)
                        print(f"Completed processing file: {completed_file}")
                if future.exception() is not None:
                    error = (future.exception(), future.result())
                    errors.append(error)
                    print(f"Error processing PDF file: {error[0]}, {error[1]}")
                    # kill the thread associated with the failed future
                    future.cancel()

        # log any errors that occurred
        if errors:
            with open("error_log.txt", "w") as f:
                for error in errors:
                    f.write(f"{error[0]}, {error[1]}\n")

    print("Finished processing all PDF files.")

# end timing function
end = time.time()
print(f"Time taken: {end - start}")
