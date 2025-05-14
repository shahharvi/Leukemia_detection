# Leukemia_detection

# 🔬 Leukemia Cancer Detection Using Routine Laboratory Parameters

## 📌 Project Overview

This project aims to develop an intelligent system for **early detection of leukemia types (ALL, AML, APL)** using **routine blood test results** and **machine learning techniques**. The objective is to assist healthcare professionals in timely diagnosis using cost-effective and accessible clinical parameters.

---

## 🚀 Features

- Predict leukemia type (ALL, AML, APL) using trained ML model
- Upload Excel sheets containing patient lab test data
- Store results in PostgreSQL database with doctor-patient mapping
- Doctor dashboard to search, view, and manage patient records
- Visual analytics for leukemia trends and type distribution
- Confidence score for each prediction

---

## 🛠️ Tech Stack

| Layer        | Technology           |
|--------------|----------------------|
| Frontend     | Python GUI / HTML (optional) |
| Backend      | **Flask** (REST API) |
| ML Model     | **LightGBM**, XGBoost |
| Data Handling| **Pandas**, NumPy    |
| Database     | **mySQL**       |
| Deployment   | Localhost / Cloud-ready |

---

## 📊 Machine Learning Model

- **Input:** Routine blood parameters i.e CBC (Complete Blood Count)
- **Output:** Leukemia Type → `ALL`, `AML`, `APL`
- **Model Used:** LightGBM Classifier
- **Accuracy Achieved:** ~92%
- **Evaluation Metrics:** Accuracy, Precision, Recall, Confusion Matrix

---

## 📁 Project Structure

leukemia_detection/
├── app.py # Main Flask app
├── model/
│ └── leukemia_model.pkl # Trained ML model
├── uploads/ # Uploaded Excel files
├── templates/
| └── leukemia_model.pkl
├── database.py # PostgreSQL connection
├── utils.py # Helper functions
├── requirements.txt # Required Python packages
└── README.md # Documentation

---

## 🧠 Model Details

- **Model Type:** LightGBM Classifier
- **Input:** Routine blood parameters (WBC, RBC, Hemoglobin, etc.)
- **Output:** Predicted Leukemia Type (ALL, AML, APL)
- **Accuracy:** ~92%
- **Evaluation Metrics:** Accuracy, Precision, Recall, Confusion Matrix

---

## ⚙️ How It Works

1. Doctor uploads an Excel sheet with patient lab results.
2. Backend extracts features using Pandas.
3. ML model predicts leukemia type with confidence.
4. Result is stored in PostgreSQL with patient and doctor details.
5. Doctor can search, filter, and view reports on a dashboard.

---

## ⚠️ Disclaimer

This project is developed for academic purposes and should not be used for real medical diagnosis without professional verification.

