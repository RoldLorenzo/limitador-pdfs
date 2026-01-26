import fitz
import requests
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional

MAX_PDF_LIMIT = 5

# Receives the path to a pdf file and a limit in MB and:
# saves it compressed in the same folder as <file_name>_compressed.pdf if compressing it is sufficient to be under the limt.
# creates a folder with the sliced compressed pdf such that each slice is under the limit.

# Returns the path where the result was saved


def save_compressed_files(input_path: str) -> str:
    directory, filename = os.path.split(input_path)
    name, ext = os.path.splitext(filename)

    compressed_bytes = compress(input_path)

    if len(compressed_bytes) > MAX_PDF_LIMIT * 1024 * 1024:
        save_split_pdf(compressed_bytes, MAX_PDF_LIMIT, name)
        return directory + "/output"
    else:
        new_filename = f"{name}_compressed{ext}"

        output_path = os.path.join(directory, new_filename)
        with open(output_path, "wb") as f:
            f.write(compressed_bytes)

        return output_path


# Creates a folder named <output_dir> and saves the sliced files inside it.


def save_split_pdf(
    pdf_bytes: bytes,
    max_size_mb: float,
    file_name: str,
    output_dir: Optional[str] = None,
) -> None:
    max_size_bytes = int(max_size_mb * 1024 * 1024)
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    if output_dir is None:
        output_dir = file_name

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    part = 1
    current_doc = fitz.open()

    for page_index in range(doc.page_count):
        current_doc.insert_pdf(doc, from_page=page_index, to_page=page_index)

        if current_doc.page_count == 1:
            continue

        current_size = len(current_doc.tobytes())

        if current_size > max_size_bytes:
            current_doc.delete_page(-1)

            output_path = output_dir / f"{file_name}_{part}.pdf"
            current_doc.save(output_path)
            current_doc.close()

            part += 1
            current_doc = fitz.open()

            current_doc.insert_pdf(doc, from_page=page_index, to_page=page_index)

    if current_doc.page_count > 0:
        output_path = output_dir / f"{file_name}_{part}.pdf"
        current_doc.save(output_path)
        current_doc.close()

    doc.close()


# Compress using iloveapi


def compress(input_path: str) -> bytes:
    load_dotenv()

    PUBLIC_KEY = os.getenv("PUBLIC_KEY")
    assert PUBLIC_KEY is not None

    r = requests.post(
        "https://api.ilovepdf.com/v1/auth",
        json={"public_key": PUBLIC_KEY},
        timeout=30,
    )
    r.raise_for_status()
    token = r.json()["token"]

    headers = {"Authorization": f"Bearer {token}"}

    r = requests.get(
        "https://api.ilovepdf.com/v1/start/compress/eu",
        headers=headers,
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()

    server = data["server"]
    task = data["task"]

    with open(input_path, "rb") as f:
        files = {"file": f}
        data = {"task": task}

        r = requests.post(
            f"https://{server}/v1/upload",
            headers=headers,
            files=files,
            data=data,
            timeout=60,
        )
        r.raise_for_status()

    upload_info = r.json()
    server_filename = upload_info["server_filename"]

    payload = {
        "task": task,
        "tool": "compress",
        "compression_level": "recommended",
        "files": [
            {
                "server_filename": server_filename,
                "filename": input_path,
            }
        ],
    }

    r = requests.post(
        f"https://{server}/v1/process",
        headers=headers,
        json=payload,
        timeout=120,
    )
    r.raise_for_status()

    r = requests.get(
        f"https://{server}/v1/download/{task}",
        headers=headers,
        timeout=120,
    )
    r.raise_for_status()

    return r.content
