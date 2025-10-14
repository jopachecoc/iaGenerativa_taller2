def leer_pdf(ruta_pdf):
    with open(ruta_pdf, "rb") as file:
        reader = PdfReader(file)
        texto = ""
        for page in reader.pages:
            texto += page.extract_text()
    return texto