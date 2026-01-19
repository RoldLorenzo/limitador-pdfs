from pdf_compressor import PdfCompressor

if __name__ == "__main__":
    compressor = PdfCompressor("teste.pdf")
    compressor.save_compressed_file("out.pdf")
