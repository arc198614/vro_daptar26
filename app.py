from flask import Flask, render_template, request, redirect, url_for, flash
import os
from datetime import datetime
from gsheet_helper import GSheetHelper

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuration
SHEET_ID = os.environ.get('GOOGLE_SHEET_ID', '11NCa_DbttL6x4Fq_oHRFooweNfNPNPq6nIlPl7OUQVU')
gsheet = None

def get_gsheet():
    global gsheet
    if gsheet is None:
        try:
            gsheet = GSheetHelper(SHEET_ID)
        except Exception as e:
            print(f"Error connecting to Google Sheets: {e}")
    return gsheet

@app.route('/')
def index():
    """Dashboard showing summary of inspections."""
    helper = get_gsheet()
    inspections = []
    if helper:
        inspections = helper.get_sheet_data('Inspections!A:E')
    
    return render_template('index.html', title="डॅशबोर्ड - ग्रा.म.अ. दप्तर तपासणी", inspections=inspections)

@app.route('/inspect', methods=['GET', 'POST'])
def inspect():
    """Form for new inspection."""
    helper = get_gsheet()
    
    if request.method == 'POST':
        # Logic to save to Google Sheets
        data = request.form.to_dict()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        inspection_id = os.urandom(4).hex()
        
        # Handle file uploads and collect links
        import tempfile
        file_links = {}
        
        # Use system temp directory (works on Vercel/Lambda)
        upload_dir = tempfile.gettempdir()
            
        for key, file in request.files.items():
            if file and file.filename:
                file_path = os.path.join(upload_dir, file.filename)
                file.save(file_path)
                
                # Upload to Google Drive (folder_id is optional)
                # DRIVE_FOLDER_ID = 'your_folder_id_here' 
                _, link = helper.upload_file(file_path)
                if link:
                    file_links[key] = link
                
                # Clean up local file
                try:
                    os.remove(file_path)
                except:
                    pass

        # Prepare summary row for 'Inspections' sheet
        # Format: ID, Saja, Name, Date, Grade, File Link
        # Taking the first link as the primary file link for the summary
        primary_link = list(file_links.values())[0] if file_links else ""
        
        row = [
            inspection_id, 
            data.get('saja_name'), 
            data.get('vro_name'), 
            timestamp, 
            "Pending",
            primary_link
        ]
        
        if helper:
            helper.append_row('Inspections!A:F', row)
            
            # Save detailed remarks to 'Compliance' sheet for each question
            for key, value in data.items():
                if key.startswith('remark_') and value.strip():
                    question_id = key.replace('remark_', '')
                    # Format: Log_ID, अधिकारी शेरा, वरिष्ठ मत, स्पष्टीकरण, स्थिती
                    # Using inspection_id as Log_ID to link them
                    compliance_row = [
                        inspection_id,
                        value, # अधिकारी शेरा (Remark)
                        "",    # वरिष्ठ मत
                        "",    # स्पष्टीकरण (GMA Explanation)
                        "Pending" # स्थिती (Status)
                    ]
                    helper.append_row('Compliance!A:E', compliance_row)
            
            print(f"Inspection {inspection_id} submitted with remarks. File links: {file_links}")
            flash('तपासणी यशस्वीरित्या जतन केली आहे!', 'success')
        else:
            flash('त्रुटी: Google Sheet कनेक्शन अयशस्वी.', 'danger')
            
        return redirect(url_for('index'))
    
    # Load questions from 'Master_Q' sheet
    questions = []
    if helper:
        questions = helper.get_sheet_data('Master_Q!A:D')
    
    # Fallback if sheet is empty or connection fails
    if not questions:
        questions = [
            {"ID": "1", "विभाग": "सामान्य", "प्रश्न": "दप्तर अद्ययावत आहे का?", "अपलोड आवश्यक": "हो"},
            {"ID": "2", "विभाग": "सामान्य", "प्रश्न": "नोंदवही पूर्ण आहे का?", "अपलोड आवश्यक": "नाही"}
        ]
        
    return render_template('inspection_form.html', questions=questions, title="नवीन तपासणी")

@app.route('/compliance', methods=['GET', 'POST'])
def compliance():
    """Compliance tracking page."""
    helper = get_gsheet()
    
    if request.method == 'POST':
        # Update compliance logic
        log_id = request.form.get('log_id')
        remark = request.form.get('remark')
        explanation = request.form.get('explanation')
        senior_remark = request.form.get('senior_remark')
        status = request.form.get('status')
        
        # Updates list for Cols C, D, E (वरिष्ठ मत, स्पष्टीकरण, स्थिती)
        updates = [senior_remark, explanation, status]
        
        if helper and helper.update_compliance_row(log_id, remark, updates):
            flash('अनुपालन यशस्वीरित्या अपडेट केले आहे!', 'success')
        else:
            flash('त्रुटी: अपडेट अयशस्वी.', 'danger')
        return redirect(url_for('compliance'))

    compliance_data = []
    if helper:
        compliance_data = helper.get_sheet_data('Compliance!A:E')
    
    return render_template('compliance.html', title="अनुपालन अहवाल", compliance_data=compliance_data)

@app.route('/reports')
def reports():
    """Reports and statistics page."""
    helper = get_gsheet()
    inspections = []
    compliance = []
    if helper:
        inspections = helper.get_sheet_data('Inspections!A:F')
        compliance = helper.get_sheet_data('Compliance!A:E')
    
    # Simple stats for reports
    stats = {
        'total': len(inspections),
        'completed': len([i for i in inspections if i.get('एकूण ग्रेड') != 'Pending']),
        'pending_compliance': len([c for c in compliance if c.get('स्थिती') == 'Pending'])
    }
    
    return render_template('reports.html', title="अहवाल आणि सांख्यिकी", stats=stats, inspections=inspections)

@app.route('/export_pdf/<inspection_id>')
def export_pdf(inspection_id):
    """Generates a PDF report for a specific inspection."""
    helper = get_gsheet()
    if not helper:
        flash("Sheet connection error", "danger")
        return redirect(url_for('index'))

    # Fetch data
    inspections = helper.get_sheet_data('Inspections!A:F')
    inspection = next((i for i in inspections if i['ID'] == inspection_id), None)
    
    if not inspection:
        flash("Inspection not found", "danger")
        return redirect(url_for('index'))

    # Fetch related compliance/remarks
    compliance = helper.get_sheet_data('Compliance!A:E')
    remarks = [c for c in compliance if c['Log_ID'] == inspection_id]

    # PDF Generation with Unicode support
    try:
        from fpdf import FPDF
        class PDF(FPDF):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                # Add Devanagari font if available, fallback to default
                font_path = 'NotoSansDevanagari-Regular.ttf'
                if os.path.isfile(font_path):
                    self.add_font('NotoSansDevanagari', '', font_path, uni=True)
                    self.set_font('NotoSansDevanagari', size=12)
                else:
                    self.set_font('Arial', size=12)
            def header(self):
                self.set_font(self.font_family, 'B', 15)
                self.cell(0, 10, 'Inspection Report - GMA System', 0, 1, 'C')
                self.ln(5)
        pdf = PDF()
        pdf.add_page()
        # Details with proper encoding
        pdf.cell(0, 10, txt=f"Inspection ID: {inspection.get('ID', '')}", ln=True)
        pdf.cell(0, 10, txt=f"Saja/Village: {inspection.get('सजा', '')}", ln=True)
        pdf.cell(0, 10, txt=f"Officer: {inspection.get('नाव', '')}", ln=True)
        pdf.cell(0, 10, txt=f"Date: {inspection.get('तारीख', '')}", ln=True)
        pdf.cell(0, 10, txt=f"Grade: {inspection.get('एकूण ग्रेड', '')}", ln=True)
        pdf.ln(10)
        pdf.set_font(pdf.font_family, 'B', 12)
        pdf.cell(0, 10, txt="Remarks & Compliance:", ln=True)
        pdf.set_font(pdf.font_family, size=10)
        for r in remarks:
            issue = r.get('अधिकारी शेरा', '')
            status = r.get('स्थिती', '')
            explanation = r.get('स्पष्टीकरण', '')
            pdf.multi_cell(0, 10, txt=f"- Issue: {issue}\n  Status: {status}\n  Explanation: {explanation}")
            pdf.ln(2)
    except Exception as e:
        # Log the error and return a user‑friendly message
        print(f"PDF generation error: {e}")
        flash('Failed to generate PDF report.', 'danger')
        return redirect(url_for('index'))

    from flask import Response
    pdf_bytes = pdf.output(dest='S').encode('utf-8')
    response = Response(pdf_bytes, mimetype='application/pdf')
    response.headers.set('Content-Disposition', 'attachment', filename=f'Report_{inspection_id}.pdf')
    return response

if __name__ == '__main__':
    app.run(debug=True)