import pdfplumber

def convert_pdf_to_md(pdf_path, md_path):
    with pdfplumber.open(pdf_path) as pdf:
        with open(md_path, 'w') as md_file:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    md_file.write(text + '\n\n---\n\n')  # Add page separator

if __name__ == "__main__":
    pdf_file = "todo/12-Month-Execution-Plan-70L-Role.pdf"
    md_file = "12-Month-Execution-Plan-70L-Role.md"
    convert_pdf_to_md(pdf_file, md_file)
    print(f"Converted {pdf_file} to {md_file}")
