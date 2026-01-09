from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
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

    # Load questions from 'Master_Q' sheet (needed for both GET and POST)
    questions = []
    if helper:
        questions = helper.get_sheet_data('Master_Q!A:D')

    # Fallback if sheet is empty or connection fails
    if not questions:
        questions = [
            {"ID": "1", "विभाग": "सामान्य", "प्रश्न": "दप्तर अद्ययावत आहे का?", "अपलोड आवश्यक": "हो"},
            {"ID": "2", "विभाग": "सामान्य", "प्रश्न": "नोंदवही पूर्ण आहे का?", "अपलोड आवश्यक": "नाही"}
        ]

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
        # Format: ID, Saja, Name, Registration Date, Date, Grade, File Link
        # Taking the first link as the primary file link for the summary
        primary_link = list(file_links.values())[0] if file_links else ""

        row = [
            inspection_id,
            data.get('saja_name'),
            data.get('vro_name'),
            data.get('registration_date'),  # Registration date
            timestamp,
            "Pending",
            primary_link
        ]

        if helper:
            helper.append_row('Inspections!A:G', row)
            
            # Save answers and remarks to 'Inspection_Answers' sheet for each question
            # First, get all question IDs from the questions list
            question_ids = [q['ID'] for q in questions] if questions else ['1', '2']

            for q_id in question_ids:
                answer = data.get(f'q_{q_id}', '')
                remark = data.get(f'remark_{q_id}', '').strip()

                # Save to Inspection_Answers sheet
                # Format: Inspection_ID, Question_ID, Answer, Remark
                answers_row = [
                    inspection_id,
                    q_id,
                    answer,
                    remark
                ]
                helper.append_row('Inspection_Answers!A:D', answers_row)

                # Also save to Compliance sheet if remark exists (for backward compatibility)
                if remark:
                    compliance_row = [
                        inspection_id,
                        remark, # अधिकारी शेरा (Remark)
                        "",     # वरिष्ठ मत
                        "",     # स्पष्टीकरण (GMA Explanation)
                        "Pending" # स्थिती (Status)
                    ]
                    helper.append_row('Compliance!A:E', compliance_row)

            print(f"Inspection {inspection_id} submitted with answers and remarks. File links: {file_links}")
            flash('तपासणी यशस्वीरित्या जतन केली आहे!', 'success')
        else:
            flash('त्रुटी: Google Sheet कनेक्शन अयशस्वी.', 'danger')
            
        return redirect(url_for('index'))

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
        inspections = helper.get_sheet_data('Inspections!A:G')
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
    inspections = helper.get_sheet_data('Inspections!A:G')
    inspection = next((i for i in inspections if i['ID'] == inspection_id), None)
    
    if not inspection:
        flash("Inspection not found", "danger")
        return redirect(url_for('index'))

    # Fetch related compliance/remarks
    compliance = helper.get_sheet_data('Compliance!A:E')
    remarks = [c for c in compliance if c['Log_ID'] == inspection_id]

    # Fetch inspection answers
    answers = helper.get_sheet_data('Inspection_Answers!A:D')
    inspection_answers = [a for a in answers if a['Inspection_ID'] == inspection_id]

    # PDF Generation with Unicode support using fpdf2
    try:
        from fpdf import FPDF

        # Create PDF with Unicode support
        pdf = FPDF()
        pdf.add_page()

        # Add Devanagari font if available
        base_dir = os.path.abspath(os.path.dirname(__file__))
        font_path = os.path.join(base_dir, 'NotoSansDevanagari-Regular.ttf')
        if os.path.isfile(font_path):
            pdf.add_font('NotoSansDevanagari', '', font_path, uni=True)
            pdf.set_font('NotoSansDevanagari', size=12)
        else:
            pdf.set_font('Arial', size=12)

        # Title
        pdf.set_font(size=15)
        pdf.cell(0, 10, 'Inspection Report - GMA System', 0, 1, 'C')
        pdf.ln(5)

        # Reset font for content
        if os.path.isfile(font_path):
            pdf.set_font('NotoSansDevanagari', size=12)
        else:
            pdf.set_font('Arial', size=12)

        # Details with proper encoding
        pdf.cell(0, 10, txt=f"Inspection ID: {inspection.get('ID', '')}", ln=True)
        pdf.cell(0, 10, txt=f"Saja/Village: {inspection.get('सजा', '')}", ln=True)
        pdf.cell(0, 10, txt=f"Officer: {inspection.get('नाव', '')}", ln=True)
        pdf.cell(0, 10, txt=f"Registration Date: {inspection.get('रुजू होण्याचा दिनांक', '')}", ln=True)
        pdf.cell(0, 10, txt=f"Inspection Date: {inspection.get('तारीख', '')}", ln=True)
        pdf.cell(0, 10, txt=f"Grade: {inspection.get('एकूण ग्रेड', '')}", ln=True)
        pdf.cell(0, 10, txt=f"File Link: {inspection.get('फाईल लिंक', '')}", ln=True)
        pdf.ln(10)

        # Add inspection answers section
        if inspection_answers:
            pdf.set_font(size=12, style='B')
            pdf.cell(0, 10, txt="Inspection Answers:", ln=True)
            pdf.set_font(size=10)
            for answer in inspection_answers:
                question_id = answer.get('Question_ID', '')
                ans = answer.get('Answer', '')
                remark = answer.get('Remark', '')
                pdf.multi_cell(0, 8, txt=f"Q{question_id}: {ans}")
                if remark:
                    pdf.multi_cell(0, 6, txt=f"  Remark: {remark}")
                pdf.ln(1)
            pdf.ln(5)

        pdf.set_font(size=12, style='B')
        pdf.cell(0, 10, txt="Remarks & Compliance:", ln=True)
        pdf.set_font(size=10)
        for r in remarks:
            issue = r.get('अधिकारी शेरा', '')
            status = r.get('स्थिती', '')
            explanation = r.get('स्पष्टीकरण', '')
            pdf.multi_cell(0, 10, txt=f"- Issue: {issue}\n  Status: {status}\n  Explanation: {explanation}")
            pdf.ln(2)
    except Exception as e:
        # Log the error and return a user‑friendly message
        print(f"PDF generation error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        flash('Failed to generate PDF report.', 'danger')
        return redirect(url_for('index'))

    from flask import Response
    pdf_bytes = pdf.output()
    response = Response(pdf_bytes, mimetype='application/pdf')
    response.headers.set('Content-Disposition', 'attachment', filename=f'Report_{inspection_id}.pdf')
    return response

@app.route('/api/inspection/<inspection_id>')
def get_inspection_details(inspection_id):
    """API endpoint to get detailed inspection information."""
    helper = get_gsheet()
    if not helper:
        return {'error': 'Database connection failed'}, 500

    try:
        # Get inspection details
        inspections = helper.get_sheet_data('Inspections!A:G')
        inspection = next((i for i in inspections if i['ID'] == inspection_id), None)

        if not inspection:
            return {'error': 'Inspection not found'}, 404

        # Get inspection answers
        answers = helper.get_sheet_data('Inspection_Answers!A:D')
        inspection_answers = [a for a in answers if a['Inspection_ID'] == inspection_id]

        # Get compliance/remarks
        compliance = helper.get_sheet_data('Compliance!A:E')
        remarks = [c for c in compliance if c['Log_ID'] == inspection_id]

        # Get uploaded files (if any)
        # Note: Files are stored as links in the Inspections sheet under 'फाईल लिंक'
        files = []
        if inspection.get('फाईल लिंक'):
            files.append({
                'name': f"Inspection_{inspection_id}_file",
                'url': inspection['फाईल लिंक']
            })

        return jsonify({
            'inspection': inspection,
            'answers': inspection_answers,
            'remarks': remarks,
            'files': files
        })

    except Exception as e:
        print(f"Error fetching inspection details: {e}")
        return {'error': 'Internal server error'}, 500

if __name__ == '__main__':
    app.run(debug=True)
