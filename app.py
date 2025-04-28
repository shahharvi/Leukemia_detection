from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
import uuid
from werkzeug.security import check_password_hash
from functools import wraps
import db  # Import our database module
from flask import json


app = Flask(__name__)
app.secret_key = "medicareleukemia123"  # Replace with a real secret key in production

# Initialize database
db.init_db()

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB in bytes (increased from 162 KB)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Add this function to check file size
def check_file_size(file, max_size_kb=5 * 1024):  # 5 MB (increased from 162 KB)
    file.seek(0, os.SEEK_END)
    file_size_kb = file.tell() / 1024
    file.seek(0)  # Reset file pointer
    return file_size_kb <= max_size_kb

# Modify the allowed_file function to include file size check
def allowed_file(file):
    filename = file.filename
    valid_extension = '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    valid_size = check_file_size(file)
    return valid_extension and valid_size


# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'doctor_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user exists and password is correct
        doctor = db.get_doctor_by_email(email)
        
        if doctor and check_password_hash(doctor['password'], password):
            # Login successful, store user info in session
            session['doctor_id'] = doctor['doctor_id']
            session['name'] = doctor['name']
            session['email'] = doctor['email']
            
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate input
        if not name or not email or not password:
            flash('All fields are required', 'error')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))
        
        # Check if user already exists
        existing_user = db.get_doctor_by_email(email)
        
        if existing_user:
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        
        # Create new doctor
        doctor_id = db.create_doctor(name, email, password)
        
        if doctor_id:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('register.html')


# In app.py
@app.route('/prediction', methods=['GET', 'POST'])
@login_required
def prediction():
    prediction_result = None
    patient_id = None
    patient_data = None
    remarks = None
    
    if request.method == 'POST':
        # Check if form submission is for adding a new patient or just adding remarks
        if 'patient_name' in request.form:
            # This is a new patient submission
            patient_name = request.form.get('patient_name')
            age = request.form.get('age')
            gender = request.form.get('gender')
            contact = request.form.get('contact', '')
            email = request.form.get('email', '')
            test_date = request.form.get('test_date')
            
            # Debug info
            print("Form data received:", request.form)
            print("Files received:", request.files)
            
            # Handle Excel file upload
            if 'blood_test_file' not in request.files:
                flash('No file part in the request', 'error')
                return redirect(request.url)
                
            file = request.files['blood_test_file']
            
            if file.filename == '':
                flash('No file selected', 'error')
                return redirect(request.url)
            
            # Check if the file extension is allowed
            filename = file.filename
            if not '.' in filename or filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
                flash('Only Excel and CSV files (.xlsx, .xls, .csv) are allowed', 'error')
                return redirect(request.url)
            
            # Check file size
            file.seek(0, os.SEEK_END)
            file_size_kb = file.tell() / 1024
            file.seek(0)  # Reset file pointer
            
            if file_size_kb > 5 * 1024:  # 5 MB limit
                flash(f'File size exceeds the limit of 5MB. Your file is {file_size_kb:.2f}KB.', 'error')
                return redirect(request.url)
            
            print(f"File received: {file.filename}, Size: {file_size_kb:.2f}KB")
            
            # Add patient with the Excel file - will update if patient exists
            patient_id = db.add_patient_with_excel(
                patient_name, age, gender, contact, email, test_date,
                file, session.get('doctor_id'), app.config['UPLOAD_FOLDER']
            )
            
            if not patient_id:
                flash('Failed to add patient or upload file', 'error')
                return redirect(request.url)
            
            print(f"Patient added/updated with ID: {patient_id}")
            
            # Get the patient data
            patient_data = db.get_patient(patient_id)
            
            if not patient_data:
                flash('Failed to retrieve patient data', 'error')
                return redirect(request.url)
            
            # Get file path to run prediction
            file_path = patient_data.get('uploaded_file')
            
            if not file_path:
                flash('File path not found in patient data', 'error')
                prediction_result = {
                    'leukemia_type': 'File path not found',
                    'confidence': 'N/A'
                }
            elif not os.path.exists(file_path):
                flash(f'File not found at path: {file_path}', 'error')
                prediction_result = {
                    'leukemia_type': 'File not found',
                    'confidence': 'N/A'
                }
            else:
                # Import prediction module
                from prediction import predict_from_file
                
                # Run actual prediction instead of using dummy data
                try:
                    prediction_result, error = predict_from_file(file_path)
                    if error:
                        flash(f'Prediction error: {error}', 'warning')
                        prediction_result = {
                            'leukemia_type': 'Error in prediction',
                            'confidence': 'N/A'
                        }
                    else:
                        # Update the patient record with prediction results
                        db.update_patient_analysis(
                            patient_id, 
                            prediction_result['leukemia_type'], 
                            float(prediction_result['confidence'].strip('%')) / 100
                        )
                        flash('Patient data and analysis completed successfully', 'success')
                except Exception as e:
                    import traceback
                    error_trace = traceback.format_exc()
                    print(f"Exception during prediction: {str(e)}")
                    print(f"Traceback: {error_trace}")
                    flash(f'Error running prediction: {str(e)}', 'error')
                    prediction_result = {
                        'leukemia_type': 'Prediction failed',
                        'confidence': 'N/A'
                    }
            
            # Get any remarks for this patient
            remarks = db.get_patient_remarks(patient_id)
            
        elif 'remark_text' in request.form and 'patient_id' in request.form:
            # This is a remark submission for an existing patient
            patient_id = request.form.get('patient_id')
            remark_text = request.form.get('remark_text')
            
            # Save the remark
            result = db.add_remark(patient_id, session['doctor_id'], remark_text)
            
            if result:
                flash('Remark added successfully', 'success')
            else:
                flash('Failed to add remark', 'error')
            
            # Get updated patient data
            patient_data = db.get_patient(patient_id)
            
            # Get or recreate the prediction result
            prediction_result = {
                'leukemia_type': patient_data['leukemia_type'] if patient_data['leukemia_type'] else 'Unknown',
                'confidence': f"{patient_data['confidence_score'] * 100:.1f}%" if patient_data['confidence_score'] else 'N/A',
            }
            
            # Get all remarks for this patient
            remarks = db.get_patient_remarks(patient_id)
    
    # For GET requests or after processing a form submission
    return render_template('prediction.html', 
                          prediction=prediction_result,
                          patient=patient_data,
                          remarks=remarks,
                          patient_id=patient_id)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    print(f"Doctor ID in session: {session.get('doctor_id')}")
    doctor_id = session['doctor_id']
    patients = db.get_doctor_patients(doctor_id)
    return render_template('dashboard.html', patients=patients)

@app.route('/api/patients/search', methods=['GET'])
@login_required
def search_patients():
    try:
        doctor_id = session['doctor_id']
        search_term = request.args.get('search', '').strip()
        leukemia_type = request.args.get('leukemia_type', '').strip()
        
        print(f"Search request - Doctor ID: {doctor_id}, Search Term: {search_term}, Leukemia Type: {leukemia_type}")
        
        patients = filter_patients(doctor_id, search_term, leukemia_type)
        
        if not patients:
            print("No patients found for this query")
            return jsonify({
                'success': True,
                'patients': [],
                'total': 0,
                'message': 'No patients found'
            }), 200
        
        print(f"Found {len(patients)} patients: {patients}")
        return jsonify({
            'success': True,
            'patients': patients,
            'total': len(patients),
            'message': 'Patients retrieved successfully'
        }), 200
    except Exception as e:
        print(f"Error in search_patients: {str(e)}")
        return jsonify({
            'success': False,
            'patients': [],
            'total': 0,
            'error': str(e)
        }), 500

# search and filter
def filter_patients(doctor_id, search_term="", leukemia_type=""):
    try:
        query = """
            SELECT 
                patient_id, 
                patient_name, 
                age, 
                gender, 
                test_date, 
                leukemia_type, 
                confidence_score,
                created_at
            FROM patients
            WHERE doctor_id = %s
        """
        params = [doctor_id]
        
        if search_term:
            search_term_clean = search_term.replace("P-", "") if search_term.startswith("P-") else search_term
            query += " AND (patient_name LIKE %s OR patient_id LIKE %s)"
            search_param = f"%{search_term}%"
            params.extend([search_param, search_param])
        
        if leukemia_type and leukemia_type.lower() != 'all':
            query += " AND leukemia_type = %s"
            params.append(leukemia_type)
        
        query += " ORDER BY created_at DESC"
        
        patients = db.execute_query(query, tuple(params), fetch=True)
        print(f"Query: {query}, Params: {params}, Result: {patients}")
        
        if patients and isinstance(patients, list) and len(patients) > 0 and not isinstance(patients[0], dict):
            keys = ['patient_id', 'patient_name', 'age', 'gender', 'test_date', 'leukemia_type', 'confidence_score', 'created_at']
            patients = [dict(zip(keys, patient)) for patient in patients]
        
        # Convert datetime objects to strings
        for patient in patients:
            if patient.get('test_date'):
                patient['test_date'] = patient['test_date'].strftime('%Y-%m-%d')
            if patient.get('created_at'):
                patient['created_at'] = patient['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        return patients if patients else []
    except Exception as e:
        print(f"Database error in filter_patients: {str(e)}")
        return []
    
@app.route('/api/patient/<patient_id>')
@login_required
def get_patient_details(patient_id):
    try:
        doctor_id = session['doctor_id']
        print(f"Fetching details for patient_id: '{patient_id}', doctor_id: {doctor_id}")
        
        patient = db.get_patient_details(patient_id)
        print(f"Patient query result: {patient}")
        
        if not patient:
            print(f"Patient not found in database for patient_id: '{patient_id}'")
            return jsonify({
                'success': False,
                'error': 'Patient not found'
            }), 404
        
        if patient.get('doctor_id') != doctor_id:
            print(f"Unauthorized access: patient doctor_id {patient.get('doctor_id')} does not match session doctor_id {doctor_id}")
            return jsonify({
                'success': False,
                'error': 'Unauthorized access'
            }), 403
        
        remarks = db.get_patient_remarks(patient_id) or []
        print(f"Patient data: {patient}, Remarks: {remarks}")
        
        response_data = {
            'success': True,
            'patient': patient,
            'remarks': remarks
        }
        print(f"Response data: {response_data}")
        return jsonify(response_data), 200
    except Exception as e:
        print(f"Error in get_patient_details: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API endpoint to get patient history
# @app.route('/api/patient/<int:patient_id>/history')
# def get_patient_history(patient_id):
#     if 'doctor_id' not in session:
#         return jsonify({"error": "Unauthorized"}), 401
    
#     doctor_id = session['doctor_id']
    
#     # Get patient history
#     history = db.get_patient_history(patient_id)
    
#     if not history:
#         return jsonify({"error": "History not found"}), 404
    
#     return jsonify(history)

# API endpoint to add a remark
@app.route('/api/patient/<int:patient_id>/remark', methods=['POST'])
def add_remark(patient_id):
    if 'doctor_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    doctor_id = session['doctor_id']
    remark_text = request.form.get('remark_text')
    
    if not remark_text:
        return jsonify({"error": "Remark text is required"}), 400
    
    # Add remark to database
    result = db.add_remark(patient_id, doctor_id, remark_text)
    
    if not result:
        return jsonify({"error": "Failed to add remark"}), 500
    
    return jsonify({"success": True, "remark_id": result})


# analytics page

# Add these routes to your app.py file

@app.route('/analytics')
@login_required
def analytics():
    # Get initial metrics
    metrics = db.get_leukemia_metrics()
    
    return render_template('analytics.html', metrics=metrics)

@app.route('/api/analytics')
@login_required
def api_analytics():
    # Get filter parameters
    date_range = request.args.get('date_range', 'all')
    leukemia_type = request.args.get('type', 'all')
    
    # Get metrics based on filters
    metrics = db.get_leukemia_metrics()
    
    # Get chart data based on filters
    monthly_data = db.get_monthly_leukemia_data(date_range, leukemia_type)
    yearly_data = db.get_yearly_leukemia_data(date_range, leukemia_type)
    weekly_data = db.get_weekly_leukemia_data(date_range, leukemia_type)
    type_distribution = db.get_leukemia_type_distribution(date_range)
    
    # Return all analytics data
    return jsonify({
        'metrics': metrics,
        'charts': {
            'monthly': monthly_data,
            'yearly': yearly_data,
            'weekly': weekly_data,
            'type_distribution': type_distribution
        }
    })


if __name__ == '__main__':
    app.run(debug=True)