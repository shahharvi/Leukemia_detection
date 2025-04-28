import os
import pickle

def check_model_files():
    """
    Check if model files exist and are properly formatted.
    """
    # Define the expected model file paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, 'model.pkl')
    scaler_path = os.path.join(base_dir, 'scaler.pkl')
    encoder_path = os.path.join(base_dir, 'encoder.pkl')
    
    print("Checking model files...")
    
    # Check if files exist
    files_status = {
        "model.pkl": os.path.exists(model_path),
        "scaler.pkl": os.path.exists(scaler_path),
        "encoder.pkl": os.path.exists(encoder_path)
    }
    
    for file_name, exists in files_status.items():
        print(f"{file_name}: {'✓ Found' if exists else '✗ Not found'}")
    
    # If any files are missing, suggest recreating them
    if not all(files_status.values()):
        print("\nSome model files are missing. You need to run model1.py to generate these files.")
        print("Make sure your CBC.csv file is in the same directory when running model1.py")
        return False
    
    # Try to load each file
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        print(f"Model loaded successfully. Type: {type(model).__name__}")
        
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        print(f"Scaler loaded successfully. Type: {type(scaler).__name__}")
        
        with open(encoder_path, 'rb') as f:
            encoder = pickle.load(f)
        print(f"Encoder loaded successfully. Type: {type(encoder).__name__}")
        
        # Get expected number of features
        n_features = scaler.n_features_in_ if hasattr(scaler, 'n_features_in_') else len(scaler.mean_)
        print(f"Model expects {n_features} features")
        
        # Get number of classes
        n_classes = len(encoder.classes_)
        print(f"Model predicts {n_classes} classes: {encoder.classes_}")
        
        return True
    except Exception as e:
        print(f"Error loading model files: {str(e)}")
        return False

if __name__ == "__main__":
    check_model_files()