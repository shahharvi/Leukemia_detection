import pickle
import numpy as np
import pandas as pd
import os

# Path to the saved model files - make these relative to the current file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'model.pkl')
SCALER_PATH = os.path.join(BASE_DIR, 'scaler.pkl')
ENCODER_PATH = os.path.join(BASE_DIR, 'encoder.pkl')

# Load the model, scaler, and encoder
# Modified function:
def load_model():
    try:
        print(f"Attempting to load model from {MODEL_PATH}")
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        print("Model loaded successfully")
        
        print(f"Attempting to load scaler from {SCALER_PATH}")
        with open(SCALER_PATH, 'rb') as f:
            scaler = pickle.load(f)
        print("Scaler loaded successfully")
        
        print(f"Attempting to load encoder from {ENCODER_PATH}")
        with open(ENCODER_PATH, 'rb') as f:
            encoder = pickle.load(f)
        print("Encoder loaded successfully")
        
        return model, scaler, encoder, None  # CHANGED: Added None as fourth return value
    except FileNotFoundError as e:
        print(f"File not found error: {e}")
        return None, None, None, f"File not found: {e}"
    except Exception as e:
        print(f"Error loading model: {e}")
        return None, None, None, f"Error loading model: {e}"

# Process the uploaded file and make predictions
def predict_from_file(file_path):
    try:
        print(f"Starting prediction with file: {file_path}")
        if not os.path.exists(file_path):
            return None, f"File not found at path: {file_path}"
            
        # Load the model components
        model, scaler, encoder, load_error = load_model()
        if model is None:
            return None, load_error or "Failed to load model"
            
        # Determine file type and read accordingly
        file_ext = os.path.splitext(file_path)[1].lower()
        print(f"File extension: {file_ext}")
        
        if file_ext == '.csv':
            data = pd.read_csv(file_path)
        elif file_ext in ['.xls', '.xlsx']:
            data = pd.read_excel(file_path)
        else:
            return None, f"Unsupported file format: {file_ext}"
            
        print(f"File loaded successfully. Columns: {data.columns.tolist()}")
        
        # Check if the data has the expected columns
        # If the expected columns aren't found, try using all numeric columns
        if 'Response' in data.columns:
            data = data.drop('Response', axis=1)
        
        # Use all numeric columns if we're not sure which ones to use
        numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
        if not numeric_cols:
            return None, "No numeric columns found in the data"
            
        print(f"Using columns for prediction: {numeric_cols}")
        
        # Preprocess the data
        X = data[numeric_cols]
        
        # Handle missing values
        X = X.fillna(X.mean())
        
        # Check if X has the right number of features expected by the scaler
        scaler_n_features = scaler.n_features_in_ if hasattr(scaler, 'n_features_in_') else len(scaler.mean_)
        print(f"Scaler expects {scaler_n_features} features, data has {X.shape[1]} features")
        
        if X.shape[1] != scaler_n_features:
            return None, f"Data has {X.shape[1]} features but model expects {scaler_n_features} features"
        
        # Scale the data
        X_scaled = scaler.transform(X)
        
        # Make prediction
        pred_proba = model.predict_proba(X_scaled)
        pred_class_idx = np.argmax(pred_proba, axis=1)
        
        # Get the class label and confidence score
        leukemia_type = encoder.inverse_transform(pred_class_idx)[0]
        confidence_score = np.max(pred_proba, axis=1)[0]
        
        print(f"Prediction successful: {leukemia_type} with confidence {confidence_score:.2f}")
        
        result = {
            'leukemia_type': leukemia_type,
            'confidence': f"{confidence_score * 100:.1f}%",
            'raw_probabilities': pred_proba[0].tolist()
        }
        
        return result, None
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error during prediction: {str(e)}")
        print(f"Traceback: {error_trace}")
        return None, f"Error during prediction: {str(e)}"