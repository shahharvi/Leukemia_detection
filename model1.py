# save_model.py
import pickle
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from lightgbm import early_stopping

# Load your data
data = pd.read_csv('CBC.csv')
data = data.dropna()

# Separate independent and dependent columns
X = data.drop('Response', axis=1)
y = data['Response']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Encode the target variable
from sklearn.preprocessing import LabelEncoder
encoder = LabelEncoder()
y_train_encoded = encoder.fit_transform(y_train)
y_test_encoded = encoder.transform(y_test)

# Initialize the LightGBM model
model = lgb.LGBMClassifier(
    objective='multiclass',
    num_class=len(np.unique(y_train_encoded)),
    learning_rate=0.05,
    n_estimators=100,
    boosting_type='gbdt',
    num_leaves=31
)

# Train the model
model.fit(
    X_train_scaled,
    y_train_encoded,
    eval_set=[(X_train_scaled, y_train_encoded), (X_test_scaled, y_test_encoded)],
    eval_names=['train', 'valid'],
    eval_metric='multi_logloss',
    callbacks=[early_stopping(stopping_rounds=10)]
)

# Make predictions
y_pred = model.predict(X_test_scaled)


from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Evaluate the model
accuracy = accuracy_score(y_test_encoded, y_pred)
# Confusion Matrix
cm = confusion_matrix(y_test_encoded, y_pred)
print(f'Accuracy: {accuracy:.2f}')
print("Classification Report:")
print(classification_report(y_test_encoded, y_pred, target_names=['ALL', 'AML', 'APL']))
print("Confusion Matrix:")
print(cm)

# Feature importance
importance_df = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values(by='importance', ascending=False)


print("Feature Importances:")
print(importance_df)


# Save the model and scaler
with open('model.pkl', 'wb') as file:
    pickle.dump(model, file)

with open('scaler.pkl', 'wb') as file:
    pickle.dump(scaler, file)

print("Model and scaler saved successfully!")

# Optional: Save the encoder as well if you want to use it for decoding predictions
with open('encoder.pkl', 'wb') as file:
    pickle.dump(encoder, file)