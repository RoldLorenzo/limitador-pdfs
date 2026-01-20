import pdf

if __name__ == "__main__":
    input = "teste.pdf"

    document_bytes = pdf.compressed(input)
    with open("out_bytes.pdf", "wb") as file:
        file.write(document_bytes)
