@ECHO OFF
rem Add tesseract ocr program to PATH
set PATH = %PATH%;.\Tesseract-OCR
rem run python script
python process.py
