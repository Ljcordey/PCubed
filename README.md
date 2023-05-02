# CRUMBS - Cleaned and Refactored OCR, NLP and Unconnected Media-Based System
Welcome to the GitHub repository for our PDF text extraction and keyword filtering project! This project uses OCR and multiprocessing to extract text from PDF files and filter it based on a predefined list of keywords. Our goal is to provide a simple and efficient solution for extracting and filtering text from large volumes of PDF files.

## Features

    OCR engine to extract text from PDF files
    Multiprocessing to speed up processing
    Keyword filtering to keep only relevant information
    Open source libraries only
    Airgapped system compatibility
    NLP-based processing to improve keyword filtering accuracy
    Code refactoring for better maintainability and scalability

## How to Use

To use this project, simply clone the repository and run the pdf_extraction.py script. Make sure to set up the necessary dependencies and specify the input and output directories as needed. You can also modify the list of keywords to match your specific use case.

## Code description

This script processes all PDF files in a specified directory and extracts their text content using OCR. The dependencies imported are: tempfile, concurrent.futures, cv2 (OpenCV), multiprocessing, numpy, pathlib, pytesseract, sqlite3, sys, time, os, and queue.

 The OCR engine used is Tesseract, and the output is stored in a SQLite database.

 The process_pdf() function is defined to process each PDF file.

 It converts each page of the PDF to an image and uses OpenCV to threshold the image to remove noise. Then, it uses pytesseract to extract text from the image.

 The extracted text is then stored in the SQLite database along with the PDF file name and page number. The image file is saved temporarily and then deleted to save disk space.

 The processing is done using multiprocessing to speed up the process, and the completed files are logged in a Queue to keep track of the progress. The errors that occurred during processing are logged in an error_log.txt file. Finally, the time taken for the processing is logged.

## Future Improvements

    Improve NLP-based processing to better identify relevant keywords
    Implement more advanced filtering techniques, such as topic modeling or sentiment analysis
    Refactor the code to improve modularity and readability
    Add unit tests and documentation to ensure code quality and ease of use
    
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

Thank you for checking out our project! If you have any questions or suggestions, please feel free to reach out.