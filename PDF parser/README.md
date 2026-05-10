# PDF Surname Extractor

Extract surnames from scanned electoral roll PDFs and get an Excel file with surname frequency counts.

## Features

- ✅ Upload up to 50 PDFs at once
- ✅ Automatic OCR for scanned PDFs
- ✅ Extracts surname (last word of Name field)
- ✅ Case-insensitive surname matching
- ✅ Hyphenated surnames count as one
- ✅ Validates extraction (warns if counts don't match expected records)
- ✅ Generates Excel file with one sheet per PDF
- ✅ Web interface - no technical knowledge needed

## Quick Start (Replit)

1. **Fork this repo to Replit**
   - Go to https://replit.com
   - Click "Create" → "Import from GitHub"
   - Paste this repo URL

2. **Install dependencies**
   - Replit will auto-detect `requirements.txt`
   - Click "Run" - it installs packages automatically

3. **Start the app**
   - Click "Run" button
   - Copy the URL from the console (e.g., `https://yourreplit.replit.dev`)
   - Share with your friend

4. **Use it**
   - Friend opens the URL in browser
   - Drag & drop up to 50 PDFs
   - Click "Process PDFs"
   - Excel file downloads automatically

## How It Works

1. **OCR**: Converts scanned PDF images to searchable text
2. **Name Extraction**: Finds all "Name :" fields in text
3. **Surname Extraction**: Takes the last word from each name
4. **Normalization**: 
   - Case-insensitive ("Dessai" = "dessai")
   - Hyphenated treated as one ("Silva-Gomes" = "silva-gomes")
   - Different spellings counted separately ("Dessai" ≠ "Desai")
5. **Excel Generation**: Creates file with one sheet per PDF

## Expected PDF Format

- Electoral roll PDFs with numbered boxes (1 to N)
- Each box contains fields: Name, Father's Name, House Number, Age, Gender
- **Only "Name" field is processed**
- Other fields are ignored

## Warnings

The app will warn you if:
- A PDF has fewer surnames extracted than expected boxes
- This might indicate OCR errors or formatting issues

## Local Testing (Windows/Mac/Linux)

```bash
# Install Python 3.8+
# Clone repo
git clone <repo-url>
cd pdf-surname-extractor

# Install dependencies
pip install -r requirements.txt

# Install Tesseract OCR
# Windows: https://github.com/UB-Mannheim/tesseract/wiki
# Mac: brew install tesseract
# Linux: sudo apt-get install tesseract-ocr

# Run app
python app.py

# Visit http://localhost:5000
```

## Limitations

- Max 50 files per upload (increase in app.py if needed)
- 500MB total file size limit
- Requires stable internet (for Replit version)
- OCR accuracy depends on PDF quality

## Technical Stack

- **Backend**: Flask
- **OCR**: Tesseract (via pytesseract)
- **PDF Processing**: PyMuPDF
- **Excel Generation**: Pandas + openpyxl
- **Frontend**: HTML5 + CSS3 + Vanilla JS

## Troubleshooting

**"No names found in PDF"**
- PDF might be corrupted
- OCR failed (try locally with higher resolution)
- Names formatted differently than expected

**"Count doesn't match"**
- OCR extraction errors on poor-quality scans
- Text might be overlapping or distorted
- Review PDF quality

**Replit timeout (>15 mins)**
- Use local installation for batch processing
- Or upload fewer PDFs at once

## For Your Friend

Just share the Replit URL. They need to:
1. Go to the URL
2. Upload PDFs (click or drag)
3. Click "Process"
4. Download Excel

No installation required.

## License

Free to use and modify.
