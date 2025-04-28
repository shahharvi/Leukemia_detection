import mysql.connector
from mysql.connector import pooling
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os

# MySQL connection configuration
db_config = {
    'host': 'localhost',
    'user': 'root',  # Replace with your MySQL username
    'password': '',  # Replace with your MySQL password
    'database': 'medicare_db'  # Your database name
}

# Create a connection pool
connection_pool = None

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def create_pool():
    global connection_pool
    try:
        connection_pool = pooling.MySQLConnectionPool(
            pool_name="medicare_pool",
            pool_size=5,
            **db_config
        )
        print("Connection pool created successfully")
        return True
    except mysql.connector.Error as err:
        print(f"Error creating connection pool: {err}")
        return False

def get_db_connection():
    global connection_pool
    if connection_pool is None:
        create_pool()
    
    try:
        connection = connection_pool.get_connection()
        return connection
    except mysql.connector.Error as err:
        print(f"Error getting connection from pool: {err}")
        return None

def create_database():
    try:
        # Connect to MySQL server without specifying a database
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password']
        )
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['database']}")
        print(f"Database '{db_config['database']}' created or already exists")
        
        conn.close()
        return True
    except mysql.connector.Error as err:
        print(f"Error creating database: {err}")
        return False

def init_db():
    # First create the database if it doesn't exist
    if not create_database():
        return False
    
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Create doctors table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            doctor_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        

        cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        patient_id VARCHAR(20) NOT NULL,
        patient_name VARCHAR(100) NOT NULL,
        age INT NOT NULL,
        gender VARCHAR(10) NOT NULL,
        contact VARCHAR(15),
        email VARCHAR(100),
        test_date DATE NOT NULL,
        uploaded_file TEXT,
        leukemia_type VARCHAR(10),
        confidence_score FLOAT,
        doctor_id INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (patient_id),
        FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
    )
''')


        
        # Create remarks table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS remarks (
            remark_id INT AUTO_INCREMENT PRIMARY KEY,
            patient_id VARCHAR(20) NOT NULL,
            doctor_id INT NOT NULL,
            remark_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
            FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
        )
        ''')
        
        conn.commit()
        conn.close()
        
        print("Database initialized successfully!")
        return True
    except mysql.connector.Error as err:
        print(f"Error initializing database: {err}")
        return False

# Helper function to execute queries
def execute_query(query, params=None, fetch=False):
    conn = get_db_connection()
    result = None
    
    if conn is None:
        return False if not fetch else None
        
    try:
        cursor = conn.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        if fetch:
            result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.lastrowid
            
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error executing query: {err}")
        if not fetch:
            conn.rollback()
        result = None if fetch else False
    finally:
        conn.close()
        
    return result

# Create a new doctor
def create_doctor(name, email, password):
    hashed_password = generate_password_hash(password)
    query = "INSERT INTO doctors (name, email, password) VALUES (%s, %s, %s)"
    return execute_query(query, (name, email, hashed_password))

# Get doctor by email
def get_doctor_by_email(email):
    query = "SELECT * FROM doctors WHERE email = %s"
    result = execute_query(query, (email,), fetch=True)
    return result[0] if result else None


def get_next_patient_id():
    """
    Generate the next patient ID in the format P-<number>
    
    Returns:
        New patient ID string
    """
    query = "SELECT patient_id FROM patients ORDER BY CAST(SUBSTRING(patient_id, 3) AS UNSIGNED) DESC LIMIT 1"
    result = execute_query(query, fetch=True)
    
    if result and result[0]['patient_id']:
        # Extract number from the last ID and increment
        last_id = result[0]['patient_id']
        try:
            # Try to treat it as a string with P- format
            if isinstance(last_id, str) and '-' in last_id:
                num = int(last_id.split('-')[1])
            else:
                # If it's an integer or doesn't have the expected format
                num = int(last_id) if isinstance(last_id, int) else 1
        except (ValueError, IndexError):
            # If any parsing error occurs, default to 1
            num = 1
        next_num = num + 1
    else:
        # Start with 1 if no patients exist
        next_num = 1
        
    return f"P-{next_num}"


def add_patient_with_excel(patient_name, age, gender, contact, email, test_date, file, doctor_id, upload_folder):
    """
    Add a patient with the associated Excel file. If the patient already exists,
    update their record instead of creating a new one.
    
    Args:
        patient_name, age, gender: Patient details
        contact, email: Contact information
        test_date: Date of the test
        file: The uploaded file object
        doctor_id: ID of the doctor creating the record
        upload_folder: Folder to save the file
        
    Returns:
        Patient ID if successful, None otherwise
    """
    # First, check if this patient already exists
    query = "SELECT patient_id FROM patients WHERE patient_name = %s AND doctor_id = %s"
    existing_patient = execute_query(query, (patient_name, doctor_id), fetch=True)
    
    # Save the file
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        new_filename = f"{timestamp}_{filename}"
        
        file_path = os.path.join(upload_folder, new_filename)
        file.save(file_path)
        
        if existing_patient:
            # Patient exists, update their record
            patient_id = existing_patient[0]['patient_id']
            
            # Update patient data
            query = '''
            UPDATE patients 
            SET age = %s, gender = %s, contact = %s, email = %s, 
                test_date = %s, uploaded_file = %s
            WHERE patient_id = %s
            '''
            execute_query(query, (age, gender, contact, email, test_date, file_path, patient_id))
            
            return patient_id
        else:
            # Generate the next patient ID for a new patient
            patient_id = get_next_patient_id()
            
            # Insert patient data
            query = '''
            INSERT INTO patients (patient_id, patient_name, age, gender, contact, email, test_date, uploaded_file, doctor_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            execute_query(query, (patient_id, patient_name, age, gender, contact, email, test_date, file_path, doctor_id))
            
            return patient_id
    
    return None

def update_patient_analysis(patient_id, leukemia_type, confidence_score):
    """
    Update patient record with leukemia analysis results
    
    Args:
        patient_id: ID of the patient to update
        leukemia_type: Type of leukemia detected
        confidence_score: Confidence score of the prediction (0.0 to 1.0)
        
    Returns:
        True if successful, False otherwise
    """
    query = '''
    UPDATE patients 
    SET leukemia_type = %s, confidence_score = %s 
    WHERE patient_id = %s
    '''
    result = execute_query(query, (leukemia_type, confidence_score, patient_id))
    return result is not False

def get_patient(patient_id, doctor_id=None):
    if doctor_id:
        query = "SELECT * FROM patients WHERE patient_id = %s AND doctor_id = %s"
        result = execute_query(query, (patient_id, doctor_id), fetch=True)
    else:
        query = "SELECT * FROM patients WHERE patient_id = %s"
        result = execute_query(query, (patient_id,), fetch=True)
    
    return result[0] if result else None

def get_patient_remarks(patient_id):
    query = '''
    SELECT r.*, d.name as doctor_name 
    FROM remarks r 
    JOIN doctors d ON r.doctor_id = d.doctor_id 
    WHERE r.patient_id = %s 
    ORDER BY r.created_at DESC
    '''
    return execute_query(query, (patient_id,), fetch=True)

# Excel file handling functions
def allowed_file(filename):
    """Check if the file has an allowed Excel extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def handle_excel_upload(file, upload_folder):
    """
    Handles the uploading of Excel files
    
    Args:
        file: The file object from the request
        upload_folder: The folder where files will be stored
        
    Returns:
        The filename if upload is successful, None otherwise
    """
    if file and allowed_file(file.filename):
        # Secure the filename to prevent security issues
        filename = secure_filename(file.filename)
        
        # Add timestamp to filename to make it unique
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_parts = os.path.splitext(filename)
        new_filename = f"{file_parts[0]}_{timestamp}{file_parts[1]}"
        
        # Ensure upload directory exists
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        # Save the file
        file_path = os.path.join(upload_folder, new_filename)
        file.save(file_path)
        
        return new_filename
    return None


# Add a remark
def add_remark(patient_id, doctor_id, remark_text):
    query = "INSERT INTO remarks (patient_id, doctor_id, remark_text) VALUES (%s, %s, %s)"
    return execute_query(query, (patient_id, doctor_id, remark_text))

def get_doctor_patients(doctor_id):
    """
    Get all patients for a specific doctor
    
    Args:
        doctor_id: ID of the doctor
        
    Returns:
        List of patient records
    """
    query = """
    SELECT 
        p.patient_id, 
        p.patient_name, 
        p.age, 
        p.gender, 
        p.test_date, 
        p.leukemia_type, 
        p.confidence_score,
        p.created_at
    FROM patients p
    WHERE p.doctor_id = %s
    ORDER BY p.created_at DESC
    """
    return execute_query(query, (doctor_id,), fetch=True)

def get_patient_details(patient_id):
    try:
        # Trim the patient_id to handle potential spaces
        patient_id = patient_id.strip()
        query = """
            SELECT patient_id, patient_name, age, gender, contact, email, test_date, 
                   leukemia_type, confidence_score, doctor_id, created_at
            FROM patients
            WHERE patient_id = %s
        """
        print(f"Executing query: {query} with patient_id: '{patient_id}'")
        result = execute_query(query, (patient_id,), fetch=True)
        print(f"Query result: {result}")
        
        if result and len(result) > 0:
            keys = ['patient_id', 'patient_name', 'age', 'gender', 'contact', 'email', 'test_date', 
                    'leukemia_type', 'confidence_score', 'doctor_id', 'created_at']
            patient = dict(zip(keys, result[0]))
            # Convert datetime objects to strings
            if patient.get('test_date'):
                patient['test_date'] = patient['test_date'].strftime('%Y-%m-%d')
            if patient.get('created_at'):
                patient['created_at'] = patient['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            return patient
        return None
    except Exception as e:
        print(f"Error in get_patient_details (db): {str(e)}")
        return None
    
def get_patient_remarks(patient_id):
    try:
        patient_id = patient_id.strip()
        query = "SELECT remark_text, created_at FROM remarks WHERE patient_id = %s ORDER BY created_at DESC"
        print(f"Executing query: {query} with patient_id: '{patient_id}'")
        result = execute_query(query, (patient_id,), fetch=True)
        print(f"Remarks query result: {result}")
        
        if result:
            remarks = [{'remark_text': row[0], 'created_at': row[1]} for row in result]
            for remark in remarks:
                if remark.get('created_at'):
                    remark['created_at'] = remark['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            return remarks
        return []
    except Exception as e:
        print(f"Error in get_patient_remarks (db): {str(e)}")
        return []

# def get_patient_history(patient_id):
#     """
#     Get historical test records for a patient
    
#     Args:
#         patient_id: ID of the patient
        
#     Returns:
#         List of historical records
#     """
#     query = """
#     SELECT 
#         r.created_at as test_date,
#         'Blood Test' as test_type,
#         p.leukemia_type,
#         p.confidence_score,
#         p.uploaded_file
#     FROM patients p
#     LEFT JOIN remarks r ON p.patient_id = r.patient_id
#     WHERE p.patient_id = %s
#     ORDER BY r.created_at DESC
#     """
#     return execute_query(query, (patient_id,), fetch=True)



# analytics functions


def get_leukemia_metrics():
    """
    Get metrics for leukemia cases
    
    Returns:
        Dictionary containing counts of different types of leukemia cases
    """
    query = """
    SELECT 
        COUNT(*) as total_cases,
        SUM(CASE WHEN leukemia_type = 'ALL' THEN 1 ELSE 0 END) as all_cases,
        SUM(CASE WHEN leukemia_type = 'AML' THEN 1 ELSE 0 END) as aml_cases,
        SUM(CASE WHEN leukemia_type = 'APL' THEN 1 ELSE 0 END) as apl_cases
    FROM patients
    WHERE leukemia_type IS NOT NULL
    """
    result = execute_query(query, fetch=True)
    return result[0] if result else {
        'total_cases': 0,
        'all_cases': 0,
        'aml_cases': 0,
        'apl_cases': 0
    }

def get_monthly_leukemia_data(date_range="all", leukemia_type="all"):
    """
    Get monthly data for leukemia cases
    
    Args:
        date_range: Filter by date range (last30, last90, last180, last365, all)
        leukemia_type: Filter by leukemia type (ALL, AML, APL, all)
        
    Returns:
        Dictionary containing monthly data for each leukemia type
    """
    # Prepare date filter
    date_filter = ""
    if date_range == "last30":
        date_filter = "AND test_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)"
    elif date_range == "last90":
        date_filter = "AND test_date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)"
    elif date_range == "last180":
        date_filter = "AND test_date >= DATE_SUB(CURDATE(), INTERVAL 180 DAY)"
    elif date_range == "last365":
        date_filter = "AND test_date >= DATE_SUB(CURDATE(), INTERVAL 365 DAY)"
    
    # Prepare type filter
    type_filter = ""
    if leukemia_type != "all":
        type_filter = f"AND leukemia_type = '{leukemia_type}'"
    
    query = f"""
    SELECT 
        DATE_FORMAT(test_date, '%Y-%m') as month,
        SUM(CASE WHEN leukemia_type = 'ALL' THEN 1 ELSE 0 END) as all_cases,
        SUM(CASE WHEN leukemia_type = 'AML' THEN 1 ELSE 0 END) as aml_cases,
        SUM(CASE WHEN leukemia_type = 'APL' THEN 1 ELSE 0 END) as apl_cases
    FROM patients
    WHERE leukemia_type IS NOT NULL {date_filter} {type_filter}
    GROUP BY DATE_FORMAT(test_date, '%Y-%m')
    ORDER BY month ASC
    """
    
    results = execute_query(query, fetch=True)
    
    # Prepare data structure
    data = {
        'labels': [],
        'all': [],
        'aml': [],
        'apl': []
    }
    
    for row in results:
        data['labels'].append(row['month'])
        data['all'].append(row['all_cases'])
        data['aml'].append(row['aml_cases'])
        data['apl'].append(row['apl_cases'])
    
    return data

def get_yearly_leukemia_data(date_range="all", leukemia_type="all"):
    """
    Get yearly data for leukemia cases
    
    Args:
        date_range: Filter by date range (not used for yearly data but kept for consistency)
        leukemia_type: Filter by leukemia type (ALL, AML, APL, all)
        
    Returns:
        Dictionary containing yearly data for each leukemia type
    """
    # Prepare type filter
    type_filter = ""
    if leukemia_type != "all":
        type_filter = f"AND leukemia_type = '{leukemia_type}'"
    
    query = f"""
    SELECT 
        YEAR(test_date) as year,
        SUM(CASE WHEN leukemia_type = 'ALL' THEN 1 ELSE 0 END) as all_cases,
        SUM(CASE WHEN leukemia_type = 'AML' THEN 1 ELSE 0 END) as aml_cases,
        SUM(CASE WHEN leukemia_type = 'APL' THEN 1 ELSE 0 END) as apl_cases
    FROM patients
    WHERE leukemia_type IS NOT NULL {type_filter}
    GROUP BY YEAR(test_date)
    ORDER BY year ASC
    """
    
    results = execute_query(query, fetch=True)
    
    # Prepare data structure
    data = {
        'labels': [],
        'all': [],
        'aml': [],
        'apl': []
    }
    
    for row in results:
        data['labels'].append(str(row['year']))
        data['all'].append(row['all_cases'])
        data['aml'].append(row['aml_cases'])
        data['apl'].append(row['apl_cases'])
    
    return data

def get_weekly_leukemia_data(date_range="all", leukemia_type="all"):
    """
    Get weekly data for leukemia cases
    
    Args:
        date_range: Filter by date range (last30, last90, last180, last365, all)
        leukemia_type: Filter by leukemia type (ALL, AML, APL, all)
        
    Returns:
        Dictionary containing weekly data for each leukemia type
    """
    # Prepare date filter
    date_filter = ""
    if date_range == "last30":
        date_filter = "AND test_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)"
    elif date_range == "last90":
        date_filter = "AND test_date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)"
    elif date_range == "last180":
        date_filter = "AND test_date >= DATE_SUB(CURDATE(), INTERVAL 180 DAY)"
    elif date_range == "last365":
        date_filter = "AND test_date >= DATE_SUB(CURDATE(), INTERVAL 365 DAY)"
    
    # Prepare type filter
    type_filter = ""
    if leukemia_type != "all":
        type_filter = f"AND leukemia_type = '{leukemia_type}'"
    
    query = f"""
    SELECT 
        CONCAT(YEAR(test_date), '-', WEEK(test_date)) as week,
        SUM(CASE WHEN leukemia_type = 'ALL' THEN 1 ELSE 0 END) as all_cases,
        SUM(CASE WHEN leukemia_type = 'AML' THEN 1 ELSE 0 END) as aml_cases,
        SUM(CASE WHEN leukemia_type = 'APL' THEN 1 ELSE 0 END) as apl_cases
    FROM patients
    WHERE leukemia_type IS NOT NULL {date_filter} {type_filter}
    GROUP BY YEAR(test_date), WEEK(test_date)
    ORDER BY YEAR(test_date) ASC, WEEK(test_date) ASC
    LIMIT 12
    """
    
    results = execute_query(query, fetch=True)
    
    # Prepare data structure
    data = {
        'labels': [],
        'all': [],
        'aml': [],
        'apl': []
    }
    
    for row in results:
        data['labels'].append(f"Week {row['week'].split('-')[1]}")
        data['all'].append(row['all_cases'])
        data['aml'].append(row['aml_cases'])
        data['apl'].append(row['apl_cases'])
    
    return data

def get_leukemia_type_distribution(date_range="all"):
    """
    Get distribution of leukemia types
    
    Args:
        date_range: Filter by date range (last30, last90, last180, last365, all)
        
    Returns:
        Dictionary containing count for each leukemia type
    """
    # Prepare date filter
    date_filter = ""
    if date_range == "last30":
        date_filter = "AND test_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)"
    elif date_range == "last90":
        date_filter = "AND test_date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)"
    elif date_range == "last180":
        date_filter = "AND test_date >= DATE_SUB(CURDATE(), INTERVAL 180 DAY)"
    elif date_range == "last365":
        date_filter = "AND test_date >= DATE_SUB(CURDATE(), INTERVAL 365 DAY)"
    
    query = f"""
    SELECT 
        SUM(CASE WHEN leukemia_type = 'ALL' THEN 1 ELSE 0 END) as all_cases,
        SUM(CASE WHEN leukemia_type = 'AML' THEN 1 ELSE 0 END) as aml_cases,
        SUM(CASE WHEN leukemia_type = 'APL' THEN 1 ELSE 0 END) as apl_cases
    FROM patients
    WHERE leukemia_type IS NOT NULL {date_filter}
    """
    
    result = execute_query(query, fetch=True)
    
    if result:
        return {
            'all': result[0]['all_cases'],
            'aml': result[0]['aml_cases'],
            'apl': result[0]['apl_cases']
        }
    
    return {
        'all': 0,
        'aml': 0,
        'apl': 0
    }

# Call this function to initialize the database when the app starts
if __name__ == "__main__":
    init_db()