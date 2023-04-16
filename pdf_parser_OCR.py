import pytesseract
import PyPDF2

# Set up the OCR engine
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Change the path to the Tesseract OCR executable to match your system 

""" # Set up the database connection
conn = sqlite3.connect('pdf_database.db')
c = conn.cursor()

# Create the table to store the PDF data
c.execute('CREATE TABLE IF NOT EXISTS pdf_data (id INTEGER PRIMARY KEY, file_name TEXT, text_data TEXT)')
# Set up the directory path to the PDF files
pdf_directory = 'test_pdf/'

# Loop through the PDF files in the directory
for file_name in os.listdir(pdf_directory):
    if file_name.endswith('.pdf'):
        # Open the PDF file and extract the text data
        with open(pdf_directory + file_name, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text_data = ''
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text_data += page.extract_text()
                
            # Clean up the text data
            text_data = re.sub(r'\n', ' ', text_data)  # Replace line breaks with spaces
            text_data = re.sub(r'\s+', ' ', text_data)  # Replace multiple spaces with single spaces
            
            # Insert the PDF data into the database
            c.execute('INSERT INTO pdf_data (file_name, text_data) VALUES (?, ?)', (file_name, text_data))
            conn.commit()

# Close the database connection
conn.close() """

def extract_image_from_pdf():
    pdf_file = open('bank_linth_-_executed_npa_and_sof_0.pdf', 'rb')
    read_pdf = PyPDF2.PdfReader(pdf_file)
    number_of_pages = len(reader.pages)
    image_counter = 1
    for page_number in range(number_of_pages):
        page = read_pdf.getPage(page_number)
        page_content = page.extractText()
        print(page_content)
        page_content = page_content.encode('utf-8')
        filename = "page_"+str(image_counter)+".jpg"
        image_counter = image_counter + 1
        with open(filename, 'wb') as f:
            f.write(page_content)
            f.close()
    pdf_file.close()
    return

def extract_text_from_image():
    text = pytesseract.image_to_string(Image.open('page_1.jpg'))
    print(text)
    return

def main():
    extract_image_from_pdf()
    extract_text_from_image()
    return 0

if __name__ == '__main__':
    main()
