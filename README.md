# 🩸 Leukemia Cancer Detection System

A lightweight diagnostic tool that predicts leukemia subtypes (**ALL**, **AML**, **APL**) using routine CBC test results and Machine Learning — empowering faster, affordable, and accessible diagnosis support.

---

## 📌 Project Highlights

- 🔍 Predict leukemia subtypes: **ALL**, **AML**, **APL**
- 📄 Upload patient test data in Excel format
- 🧠 Built with ML models: **LightGBM**, **XGBoost**
- 📈 Visual analytics of prediction trends
- 👨‍⚕️ Doctor dashboard with search, view & report features
- 💾 Stores results in a MySQL database
- ✅ Shows confidence score for every prediction

---

## ⚙️ How It Works

1. Doctor uploads patient CBC test data (Excel).
2. Data is cleaned and fed into the ML model.
3. Model predicts leukemia subtype with a confidence score.
4. Results are stored and available for viewing through the dashboard.

---

## 🛠️ Tech Stack

| Layer         | Technology                       |
|---------------|----------------------------------|
| **Frontend**  | HTML, CSS, JavaScript     |
| **Backend**   | Flask (REST API)                 |
| **ML Models** | LightGBM, XGBoost                |
| **Database**  | MySQL                            |
| **Libraries** | Pandas, NumPy, Scikit-learn      |
| **Deployment**| Localhost (Cloud-ready setup)    |

---

## 🧠 Model Overview

- **Input:** CBC parameters (WBC, RBC, Hemoglobin, Platelet, etc.)
- **Output:** Predicted Leukemia Type: `ALL`, `AML`, or `APL`
- **Training Accuracy:** ~92%
- **ML Models Used:** LightGBM & XGBoost
- **Evaluation Metrics:** Accuracy, Precision, Recall, F1-Score
  
---

## ⚠️ Disclaimer

This project is intended for academic and research purposes only. It is **not** approved for clinical use. Always consult qualified medical professionals before making any health-related decisions.

---

## 👨‍💻 Author

**Harvi Shah**  
📧 shahharvi05@gmail.com  
🔗 [LinkedIn](https://www.linkedin.com/in/harvi-shah-0918762b4/)  
🎓 B.Tech Computer Engineering | CHARUSAT

---

🧠 *"Code with care. Build with purpose."*
