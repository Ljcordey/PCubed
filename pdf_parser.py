import pytesseract
import pdfplumber

# Specify the path to the PDF file
pdf_path = "PCubed\test_pdf\vadian_npa_and_sof.pdf"

# Open the PDF file using pdfplumber
with pdfplumber.open(pdf_path) as pdf:
    # Iterate over each page of the PDF file
    for page in pdf.pages:
        # Extract the text from the page using Pytesseract
        text = pytesseract.image_to_string(page.to_image())
        # Print the text for debugging purposes
        print(text)