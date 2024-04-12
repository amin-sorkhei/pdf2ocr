import os
import shutil
import PyPDF2
import pytesseract
from pdf2image import convert_from_path
from tqdm import tqdm

import logging

logging.getLogger().setLevel(logging.INFO)


required_paths = {
    "input_pdf_path": "AEF-4 Workbook.pdf",
    "converted_pdf_to_image_path": "./pdf_images",
    "converted_images_to_pdf_path": "./converted_images_to_pdf",
}

required_paths["output_pdf_path"] = (
    required_paths["input_pdf_path"].split(".pdf")[0] + "OCR.pdf"
)

assert os.path.exists(required_paths["input_pdf_path"])

# clean ups!
for path, value in required_paths.items():
    if path in ["input_pdf_path", "output_pdf_path"]:
        # no need to delete these
        continue
    if os.path.exists(path=value):
        logging.info(f"path {path} exists, removing ....")
        shutil.rmtree(path=value)
    os.makedirs(name=value)

# read pdf pages and convert that to single image for each page
logging.info(f'Loading {required_paths["input_pdf_path"]} ...')
images = convert_from_path(required_paths["input_pdf_path"])

images_path = []
for i, image in tqdm(enumerate(images, 1)):
    image_path = os.path.join(
        required_paths["converted_pdf_to_image_path"], f"page_{i}.png"
    )
    image.save(
        image_path,
        format="PNG",
    )
    images_path.append(image_path)

logging.info(
    f"converting pages in {required_paths['converted_pdf_to_image_path']} to searchable pdfs ..."
)
pdf_paths = []
for image_path in tqdm(images_path):
    pdf = pytesseract.image_to_pdf_or_hocr(image_path, extension="pdf")
    pdf_path = os.path.join(
        required_paths["converted_images_to_pdf_path"],
        image_path.split("/")[-1].split("png")[0] + ".pdf",
    )
    with open(pdf_path, "w+b") as f:
        f.write(pdf)
    pdf_paths.append(pdf_path)


merger = PyPDF2.PdfMerger()
for pdf_path in tqdm(pdf_paths):
    merger.append(pdf_path)
merger.write(required_paths["output_pdf_path"])
