from PyPDF2 import PdfReader, PdfWriter
from pathlib import Path


class PdfCompressor:
    def __init__(self, path: Path) -> None:
        self.reader = PdfReader(path)
        self.writer = PdfWriter(path)

    # Removed from https://pypdf2.readthedocs.io/en/3.x/user/file-size.html

    # PyPDF2 supports the FlateDecode filter which uses the zlib/deflate compression method.
    # It is a lossless compression, meaning the resulting PDF looks exactly the same.
    def compress_content(self) -> None:
        for page in self.reader.pages:
            page.compress_content_streams()
            self.writer.add_page(page)

        self.writer.add_metadata(self.reader.metadata)

    def save_compressed_file(self, output_path: Path) -> None:
        self.compress_content()
        with open(output_path, "wb") as f:
            self.writer.write(f)
