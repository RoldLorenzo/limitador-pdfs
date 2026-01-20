import fitz
from PIL import Image
from io import BytesIO


def compressed(
    pdf_path: str,
    dpi: int = 150,
    quality: int = 50,
) -> bytes:
    doc = fitz.open(pdf_path)
    processed_xrefs = set()

    for page in doc:
        images = page.get_images(full=True)

        for img in images:
            xref = img[0]

            if xref in processed_xrefs:
                continue

            processed_xrefs.add(xref)

            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            image = Image.open(BytesIO(image_bytes))

            if dpi:
                scale = dpi / 300
                new_size = (
                    max(1, int(image.width * scale)),
                    max(1, int(image.height * scale)),
                )
                image = image.resize(new_size, Image.Resampling.LANCZOS)

            buffer = BytesIO()
            image.save(
                buffer,
                format="JPEG",
                quality=quality,
                optimize=True,
                progressive=True,
            )
            buffer.seek(0)

            page.replace_image(xref=xref, stream=buffer.read())

    doc_buffer = BytesIO()
    doc.save(
        doc_buffer,
        garbage=4,
        use_objstms=1,
        deflate=True,
        clean=True,
    )
    doc_buffer.seek(0)

    return doc_buffer.read()
