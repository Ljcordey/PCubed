# OCR POC for Air-gapped system

## Code description

This script processes all PDF files in a specified directory and extracts their text content using OCR. The dependencies imported are: tempfile, concurrent.futures, cv2 (OpenCV), multiprocessing, numpy, pathlib, pytesseract, sqlite3, sys, time, os, and queue.

 The OCR engine used is Tesseract, and the output is stored in a SQLite database.

 The process_pdf() function is defined to process each PDF file.

 It converts each page of the PDF to an image and uses OpenCV to threshold the image to remove noise. Then, it uses pytesseract to extract text from the image.

 The extracted text is then stored in the SQLite database along with the PDF file name and page number. The image file is saved temporarily and then deleted to save disk space.

 The processing is done using multiprocessing to speed up the process, and the completed files are logged in a Queue to keep track of the progress. The errors that occurred during processing are logged in an error_log.txt file. Finally, the time taken for the processing is logged.

```flow
st=>start: Start
op1=>operation: Set up OCR engine
op2=>operation: Specify path to PDF folder
op3=>operation: Specify path to temporary directory
op4=>operation: Create database table if not exists
op5=>operation: Define function to process a single PDF
op6=>operation: Start timing function
op7=>operation: Create list of PDF files in folder
op8=>operation: Process PDF files using multiprocessing
op9=>condition: Is multiprocessing complete?
op10=>operation: Log any errors that occurred
op11=>operation: End timing function
e=>end: Finish

st->op1->op2->op3->op4->op5->op6->op7->op8->op9
op9(yes)->op10->op11->e
op9(no)->op9
```

Specifically, here is the algorithmic diagram of the Process_pdf function.

```flow
st=>start: Start
op1=>operation: Load PDF file
op2=>operation: Convert PDF to image(s)
op3=>operation: Apply OCR to image(s)
op4=>operation: Extract text from OCR output
op5=>operation: Store text in database
e=>end: Finish

st->op1->op2->op3->op4->op5->e
```

## Libraries and Dependencies

Here are the dependencies and installation instructions for each of the Python libraries:

- `tempfile`: No dependencies needed, it's part of the Python standard library.

- `concurrent.futures`: No dependencies needed, it's part of the Python standard library starting from version 3.2.

- `cv2`: It depends on the `opencv-python` library. To install, you can run `pip install opencv-python`.

- `multiprocessing`: No dependencies needed, it's part of the Python standard library.

- `numpy`: To install, you can run `pip install numpy`.

- `pathlib`: No dependencies needed, it's part of the Python standard library starting from version 3.4.

- `pytesseract`: It depends on the Tesseract OCR engine. To install, you can run `pip install pytesseract`. However, you also need to install Tesseract OCR engine separately. You can download it from the official Tesseract OCR repository (https://github.com/tesseract-ocr/tesseract) and install it according to the instructions provided there.

- `sqlite3`: No dependencies needed, it's part of the Python standard library.

- `sys`: No dependencies needed, it's part of the Python standard library.

- `time`: No dependencies needed, it's part of the Python standard library.

- `os`: No dependencies needed, it's part of the Python standard library.

- `queue`: No dependencies needed, it's part of the Python standard library.

- `WandImage`: It depends on the ImageMagick library. To install, you can run `pip install Wand`. You also need to install ImageMagick separately. You can download it from the official ImageMagick website (https://imagemagick.org/) and install it according to the instructions provided there.

- `Color`: It's part of the `Wand` library and there are no additional dependencies needed once you have installed `Wand`.

Overall, the installation process for each library is straightforward, and most of the libraries are included in the Python standard library or can be installed using `pip`.

## Python script

> version 13.0

```python
import tempfile
import concurrent.futures
import cv2
import multiprocessing
import numpy as np
import pathlib
import pytesseract
import sqlite3
import sys
import time
import os
import queue 
from wand.image import Image as WandImage
from wand.color import Color

# Set up the OCR engine
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\loco2\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# specify path to the folder containing PDF files
pdf_folder_path = r"C:\Users\loco2\OneDrive - EY\Documents\GitHub\PCubed\test_pdf2"

# specify path to the temporary directory
temp_dir = tempfile.gettempdir()

# create the database table if it does not exist
with sqlite3.connect("pdf_text.db") as conn:
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS pdf_text (file_name TEXT, page_number INTEGER, text_content TEXT)")

# function to process a single PDF file
def process_pdf(pdf_path, output_queue):
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
                try:
                    with sqlite3.connect("pdf_text.db") as conn:
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO pdf_text (file_name, page_number, text_content) VALUES (?, ?, ?)",
                                    (pdf_path.name, i+1, text))
                        # commit the changes to the database
                        conn.commit()
                except sqlite3.Error as e:
                    print(f"Error inserting data for {pdf_path.name}: {e}")

                # save the image file in the temporary directory and delete it to save disk space
                temp_file_path = os.path.join(temp_dir, f"{pdf_path.name}-{i}.jpeg")
                cv2.imwrite(temp_file_path, threshold_image)
                os.remove(temp_file_path)

    print(f"Finished processing file: {pdf_path.name}")
    output_queue.put(pdf_path.name)
    
# start timing function
start = time.time()

# create a list of all PDF files in the folder
pdf_files = [f for f in pathlib.Path(pdf_folder_path).iterdir() if f.suffix == '.pdf']

# process the PDF files using multiprocessing
if __name__ == '__main__':
    multiprocessing.freeze_support()  # necessary for Windows platform
    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        output_queue = multiprocessing.Manager().Queue()
        futures = []
        for pdf_path in pdf_files:
            future = executor.submit(process_pdf, pdf_path, output_queue)
            futures.append(future)
        
        # wait for all futures to complete
        completed_files = set()
        errors = []
        while len(completed_files) < len(pdf_files):
            for future in concurrent.futures.as_completed(futures):
                try:
                    completed_file = output_queue.get(timeout=1)
                    completed_files.add(completed_file)
                    print(f"Completed processing file: {completed_file}")
                except queue.Empty:
                    pass

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
```

## TODO

- [x] POC is done
- [x] Multiprocessed
- [x] Uses only open source libraries
- [x] Can run on airgapped systems
- [ ] Implement keyword filtering:
  - [ ] Identify the keywords you want to keep
  - [ ] Preprocess the text
  - [ ] Tokenize the text
  - [ ] Count the frequency of the keywords
  - [ ] Filter out the unnecessary words
- [ ] further improve runtime execution:
  - [ ] improving the algorithmic processes
  - [ ] linearizing some functions
  - [ ] using GPU acceleration
  - [ ] minimizes time intensive I/O operations



