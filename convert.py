import os
import shutil
import PyPDF2
import pytesseract
from pdf2image import convert_from_path
from tqdm import tqdm  # For progress bar
import logging  # For logging messages
import argparse  # For command line argument parsing
logging.getLogger().setLevel(logging.INFO)

class PDF_OCR:
    """
    A class to perform OCR (Optical Character Recognition) on PDF files using Tesseract.
    """

    def __init__(self, input_pdf_path):
        """
        Initialize the PDF_OCR class with the input PDF path.

        Args:
            input_pdf_path (str): Path to the input PDF file.
        """
        # Define paths for input and output files
        self.required_paths = {
            "input_pdf_path": input_pdf_path,  # Path to input PDF file from command line argument
            "converted_pdf_to_image_path": "./pdf_images",  # Path to store converted images
            "converted_images_to_pdf_path": "./converted_images_to_pdf",  # Path to store converted images as PDFs
        }
        # Derive output PDF path from input PDF path
        self.required_paths["output_pdf_path"] = (
            self.required_paths["input_pdf_path"].split(".pdf")[0] + "OCR.pdf"
        )

    def clean_up_directories(self):
        """
        Clean up directories before starting the OCR process.
        """
        # Check if input PDF file exists
        assert os.path.exists(self.required_paths["input_pdf_path"])
        # Clean up directories before starting
        for path, value in self.required_paths.items():
            if path in ["input_pdf_path", "output_pdf_path"]:
                # Skip input and output paths from deletion
                continue
            if os.path.exists(path=value):
                # Remove existing directory
                logging.info(f"path {path} exists, removing ....")
                shutil.rmtree(path=value)
            # Create directories
            os.makedirs(name=value)

    def convert_images_to_pdf(self):
        """
        Convert images extracted from the input PDF into searchable PDFs using OCR.

        Returns:
            List[str]: List of paths to the converted PDF files.
        """
        # Read PDF pages and convert each page to an image
        logging.info(f'Loading {self.required_paths["input_pdf_path"]} ...')
        images = convert_from_path(self.required_paths["input_pdf_path"])
        images_path = []
        for i, image in tqdm(enumerate(images, 1), desc="Converting pages to images"):
            # Define path for each converted image
            image_path = os.path.join(
                self.required_paths["converted_pdf_to_image_path"], f"page_{i}.png"
            )
            # Save the image as PNG format
            image.save(
                image_path,
                format="PNG",
            )
            images_path.append(image_path)

        # Convert images to searchable PDFs using OCR (Optical Character Recognition)
        logging.info(
            f"Converting images in {self.required_paths['converted_pdf_to_image_path']} to searchable PDFs ..."
        )
        pdf_paths = []
        for image_path in tqdm(
            images_path, desc="Converting images to searchable PDFs"
        ):
            # Convert image to PDF
            pdf = pytesseract.image_to_pdf_or_hocr(image_path, extension="pdf")
            # Define path for the resulting PDF
            pdf_path = os.path.join(
                self.required_paths["converted_images_to_pdf_path"],
                image_path.split("/")[-1].split("png")[0] + ".pdf",
            )
            # Write the PDF data to the file
            with open(pdf_path, "w+b") as f:
                f.write(pdf)
            pdf_paths.append(pdf_path)
        return pdf_paths

    def merge_pdfs(self, pdf_paths):
        """
        Merge individual PDFs into a single output PDF.

        Args:
            pdf_paths (List[str]): List of paths to the PDF files to be merged.
        """
        # Merge individual PDFs into a single output PDF
        merger = PyPDF2.PdfMerger()
        for pdf_path in tqdm(pdf_paths, desc="Merging PDFs"):
            merger.append(pdf_path)
        # Write the merged PDF to the output file
        merger.write(self.required_paths["output_pdf_path"])
        # Logging the completion message
        logging.info("PDF OCR process completed.")


if __name__ == "__main__":

    # Initialize ArgumentParser
    parser = argparse.ArgumentParser(description="PDF OCR with Tesseract")
    parser.add_argument(
        "--input_pdf_path",
        type=str,
        help="Path to the input PDF file for OCR processing",
    )
    # Parse command line arguments
    args = parser.parse_args()
    # Create an instance of PDF_OCR class with the input PDF path
    pdf_ocr = PDF_OCR(input_pdf_path=args.input_pdf_path)
    # Clean up directories before starting OCR process
    pdf_ocr.clean_up_directories()
    # Convert images to PDFs
    pdf_paths = pdf_ocr.convert_images_to_pdf()
    # Merge PDFs into a single output PDF
    pdf_ocr.merge_pdfs(pdf_paths)
