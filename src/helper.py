import fitz  # PyMuPDF


def extract_text_from_pdf(uploaded_file):
    """
    Extract text from uploaded PDF file (Streamlit file uploader).

    Args:
        uploaded_file: Uploaded file object from Streamlit

    Returns:
        str: Extracted text from PDF
    """

    if uploaded_file is None:
        return ""

    try:
        # Open PDF from memory (no need to save file)
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")

        text = ""

        for page in doc:
            text += page.get_text("text") + "\n"

        doc.close()

        return text.strip()

    except Exception as e:
        return f"Error reading PDF: {str(e)}"








