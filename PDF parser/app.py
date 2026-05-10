from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image
import fitz
import pandas as pd
from collections import defaultdict
import os
import io
import re
from pathlib import Path

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max
app.config['UPLOAD_FOLDER'] = 'temp_uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using OCR on scanned pages"""
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            # Try to get text directly first
            page_text = page.get_text()
            if page_text.strip():
                text += page_text + "\n"
            else:
                # If no text, render as image and OCR
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                ocr_text = pytesseract.image_to_string(img)
                text += ocr_text + "\n"
    except Exception as e:
        return None, f"Error reading PDF: {str(e)}"
    return text, None

def extract_names_from_text(text):
    """Extract all names from the text using the Name: pattern"""
    names = []
    # Look for lines with "Name :" pattern
    lines = text.split('\n')
    for line in lines:
        if 'Name :' in line or 'Name:' in line:
            # Extract everything after "Name :"
            match = re.search(r'Name\s*:\s*(.+?)(?:\n|$)', line, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Clean up - remove extra spaces and special characters
                name = ' '.join(name.split())
                if name and len(name) > 2:  # Basic sanity check
                    names.append(name)
    return names

def extract_surname(name):
    """Extract surname (last word) from full name"""
    if not name:
        return None
    words = name.split()
    if len(words) > 0:
        # Handle hyphenated surnames as single word
        surname = words[-1]
        # Normalize case
        return surname.lower()
    return None

def process_pdf(pdf_path, filename):
    """Process single PDF and extract surname counts"""
    text, error = extract_text_from_pdf(pdf_path)
    if error:
        return None, error
    
    names = extract_names_from_text(text)
    
    if not names:
        return None, f"No names found in {filename}"
    
    # Count surnames
    surname_counts = defaultdict(int)
    for name in names:
        surname = extract_surname(name)
        if surname:
            surname_counts[surname] += 1
    
    # Sort by count descending
    sorted_surnames = sorted(surname_counts.items(), key=lambda x: x[1], reverse=True)
    
    result = {
        'filename': filename,
        'total_records': len(names),
        'total_counted': sum(count for _, count in sorted_surnames),
        'surnames': sorted_surnames,
        'warning': None
    }
    
    # Warn if count doesn't match
    if result['total_counted'] != result['total_records']:
        result['warning'] = f"Warning: Found {result['total_records']} names but only {result['total_counted']} surnames counted. Check for extraction issues."
    
    return result, None

def create_excel_file(results):
    """Create Excel file with one sheet per PDF"""
    excel_buffer = io.BytesIO()
    
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        for result in results:
            # Create dataframe from surnames
            df_data = {
                'Surname': [surname for surname, _ in result['surnames']],
                'Count': [count for _, count in result['surnames']]
            }
            df = pd.DataFrame(df_data)
            
            # Use filename as sheet name (max 31 chars, Excel limit)
            sheet_name = result['filename'].replace('.pdf', '')[:31]
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Add validation info as comment
            if result['warning']:
                ws = writer.sheets[sheet_name]
                ws['A1'].comment = f"Total Records: {result['total_records']}, Total Counted: {result['total_counted']}"
    
    excel_buffer.seek(0)
    return excel_buffer

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    if not files or len(files) == 0:
        return jsonify({'error': 'No files selected'}), 400
    
    if len(files) > 50:
        return jsonify({'error': 'Maximum 50 files at a time'}), 400
    
    results = []
    errors = []
    
    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            errors.append(f"{file.filename}: Not a PDF file")
            continue
        
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            result, error = process_pdf(filepath, filename)
            if error:
                errors.append(f"{filename}: {error}")
            else:
                results.append(result)
            
            # Clean up
            os.remove(filepath)
        
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")
    
    if not results:
        return jsonify({'error': 'No PDFs could be processed. ' + ' | '.join(errors)}), 400
    
    try:
        excel_file = create_excel_file(results)
        
        response_data = {
            'success': True,
            'processed': len(results),
            'warnings': [r['warning'] for r in results if r['warning']],
            'errors': errors if errors else None
        }
        
        # Return file for download
        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='surname_counts.xlsx'
        )
    
    except Exception as e:
        return jsonify({'error': f'Error creating Excel file: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
