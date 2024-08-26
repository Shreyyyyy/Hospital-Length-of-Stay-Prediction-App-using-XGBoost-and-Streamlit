# -*- coding: utf-8 -*-
"""length_of_stay_shreyans.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1t0VEQFF7CeLqtTESF0t4lgJsE2Hb89d_
"""

# !pip install streamlit
# !pip install pyngrok
# !pip install xgboost

import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error
from xgboost import XGBRegressor
import pickle
import numpy as np

# Load your dataset
df = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/ada.csv')

# Handle missing values in 'Comorbidities' by filling them with a placeholder
df['Comorbidities'].fillna('Unknown', inplace=True)

# Define independent variables (features) and dependent variable (target)
X = df.drop('Length of Stay', axis=1)
y = df['Length of Stay']

# Categorical columns for one-hot encoding
categorical_features = ['Gender', 'Admission Type', 'Primary Diagnosis',
                        'Severity of Illness', 'Comorbidities', 'Ward/Department', 'Discharge Disposition']

# Numerical columns now exclude 'Procedure Codes Count'
numerical_features = ['Age']

# Create a Column Transformer to apply transformations to the appropriate columns
preprocessor = ColumnTransformer(
    transformers=[
        ('num', 'passthrough', numerical_features),  # No scaling needed for tree-based models
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])

# Create a pipeline that first transforms the data and then fits the model
model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', XGBRegressor(random_state=42))
])

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define the hyperparameter grid for XGBoost
param_grid = {
    'regressor__n_estimators': [100, 200],
    'regressor__max_depth': [3, 5, 7],
    'regressor__learning_rate': [0.01, 0.1, 0.2],
    'regressor__subsample': [0.8, 1.0],
    'regressor__colsample_bytree': [0.8, 1.0]
}

# Perform grid search with cross-validation
grid_search = GridSearchCV(model_pipeline, param_grid, cv=5, n_jobs=-1, scoring='neg_mean_squared_error', verbose=2)

# Train the model with grid search
grid_search.fit(X_train, y_train)

# Save the best model
with open('xgb_model_pipeline.pkl', 'wb') as file:
    pickle.dump(grid_search.best_estimator_, file)

# Evaluate the model on the test set
y_pred = grid_search.best_estimator_.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)

print("XGBoost model trained and saved successfully!")
print(f"Test Set Mean Squared Error: {mse}")
print(f"Test Set Root Mean Squared Error: {rmse}")
print(f"Best Hyperparameters: {grid_search.best_params_}")

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

# 1. Distribution of Length of Stay
plt.figure(figsize=(8, 6))
sns.histplot(df['Length of Stay'], kde=True, color='skyblue')
plt.title('Distribution of Length of Stay')
plt.xlabel('Length of Stay')
plt.ylabel('Frequency')
plt.show()

# 2. Feature Importance (after model training)
# Ensure that the model has been trained before this step
best_model = grid_search.best_estimator_.named_steps['regressor']
importance = best_model.feature_importances_

# Get feature names from OneHotEncoder
onehot_columns = grid_search.best_estimator_.named_steps['preprocessor'].named_transformers_['cat'].get_feature_names_out(categorical_features)
all_features = np.concatenate([numerical_features, onehot_columns])

# Sort features by importance
sorted_idx = np.argsort(importance)

plt.figure(figsize=(10, 8))
plt.barh(range(len(sorted_idx)), importance[sorted_idx], align='center', color='purple')
plt.yticks(range(len(sorted_idx)), [all_features[i] for i in sorted_idx])
plt.xlabel('Feature Importance')
plt.title('Feature Importance for XGBoost Model')
plt.show()

# 3. Correlation Heatmap
# Select only numerical columns for the correlation matrix
plt.figure(figsize=(10, 8))
corr_matrix = df[numerical_features + ['Length of Stay']].corr()
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', linewidths=0.5)
plt.title('Correlation Heatmap')
plt.show()

# 4. Actual vs Predicted Values
y_pred = grid_search.best_estimator_.predict(X_test)

plt.figure(figsize=(8, 6))
plt.scatter(y_test, y_pred, color='green', edgecolor='k', alpha=0.7)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'k--', lw=2)
plt.title('Actual vs Predicted Length of Stay')
plt.xlabel('Actual Length of Stay')
plt.ylabel('Predicted Length of Stay')
plt.show()

# 5. Residuals Plot
residuals = y_test - y_pred

plt.figure(figsize=(8, 6))
plt.scatter(y_pred, residuals, color='red', edgecolor='k', alpha=0.7)
plt.axhline(y=0, color='black', linestyle='--')
plt.title('Residuals Plot')
plt.xlabel('Predicted Length of Stay')
plt.ylabel('Residuals')
plt.show()

"""
regressor__n_estimators: [100, 200]

Specifies the number of boosting rounds or trees to be built.
Possible values: 100 or 200 trees.

regressor__max_depth: [3, 5, 7]

Defines the maximum depth of each tree. Deeper trees can capture more complex relationships but may lead to overfitting.
Possible values: Tree depths of 3, 5, or 7.

regressor__learning_rate: [0.01, 0.1, 0.2]

Also known as the shrinkage factor. It controls how much each tree contributes to the final prediction.
A lower learning rate makes the model more robust but requires more trees.
Possible values: 0.01 (small contribution), 0.1 (moderate contribution), or 0.2 (larger contribution).

regressor__subsample: [0.8, 1.0]

Specifies the fraction of the training data to be randomly sampled for growing each tree.
A value of 0.8 means that 80% of the training data will be used to train each tree, which helps prevent overfitting.
Possible values: 0.8 (80% of data) or 1.0 (100% of data).

regressor__colsample_bytree: [0.8, 1.0]

Determines the fraction of features (columns) to be randomly
selected for each tree.
A value of 0.8 means that 80% of the features will be used for constructing each tree.
Possible values: 0.8 (80% of features) or 1.0 (100% of features)."""

# Commented out IPython magic to ensure Python compatibility.
# %%writefile ok.py
# import streamlit as st
# import pandas as pd
# import numpy as np
# import pickle
# 
# # Load the trained model
# model_pipeline = pickle.load(open('/content/xgb_model_pipeline.pkl', 'rb'))
# 
# def predict_length_of_stay():
#     # Custom CSS for styling
#     st.markdown("""
#         <style>
#             .description {
#                 font-size: 18px;
#                 font-family: 'Times New Roman', Times, serif;
#                 font-weight: bold;
#                 color: #ffffff; /* Bright white text color */
#                 text-align: center;
#                 margin-bottom: 20px;
#                 padding: 10px;
#                 background: linear-gradient(135deg, #6a82fb, #fc5c7d); /* Modern violet and pink gradient */
#                 border-radius: 10px;
#                 box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15); /* Enhanced shadow for better depth */
#                 border: 1px solid #ffffff; /* White border for a clean finish */
#             }
#             .day-box {
#                 background: linear-gradient(45deg, #f3ec78, #af4261);
#                 color: white;
#                 padding: 15px;
#                 margin-bottom: 10px;
#                 border-radius: 10px;
#                 transition: transform 0.3s ease;
#                 cursor: pointer;
#             }
#             .day-box:hover {
#                 transform: translateY(-5px);
#                 background: linear-gradient(45deg, #af4261, #f3ec78);
#             }
#             .day-title {
#                 font-weight: bold;
#                 font-size: 20px;
#             }
#         </style>
#     """, unsafe_allow_html=True)
# 
#     # Project explanation at the top
#     st.markdown("""
#     <div class="description">
#         This project predicts a patient's hospital length of stay based on their medical details,
#         including diagnosis, severity, and procedures. The system uses machine learning to assist
#         healthcare providers in planning care and resource management effectively.
#     </div>
#     """, unsafe_allow_html=True)
# 
#     st.title('🏥 Hospital Length of Stay Prediction')
#     st.markdown("""
#         ### Please fill in the patient details below to predict the hospital stay duration.
#     """)
# 
#     # Streamlit columns for better layout
#     col1, col2 = st.columns(2)
# 
#     with col1:
#         age = st.slider("🧑‍🦳 Age", min_value=0, max_value=100, value=30, step=1, help="Select the patient's age")
#         gender = st.selectbox("⚧ Gender", ['Male', 'Female','Non Binary'], help="Select the patient's gender")
#         admission_type = st.selectbox("🏥 Admission Type", ['Emergency', 'Elective', 'Urgent'], help="Select the type of admission")
# 
#     with col2:
#         primary_diagnosis = st.selectbox("🩺 Primary Diagnosis", [
#             'Diabetes', 'Hypertension', 'Asthma', 'Heart Disease', 'Chronic Obstructive Pulmonary Disease (COPD)',
#             'Kidney Disease', 'Stroke', 'Liver Disease', 'Pneumonia', 'Cancer', 'Dementia', 'Anemia', 'Arthritis',
#             'Obesity', 'Sepsis', 'COVID-19', 'Fracture'], help="Select the patient's primary diagnosis")
#         severity_of_illness = st.selectbox("🩸 Severity of Illness", ['Mild', 'Moderate', 'Severe'], help="Select the severity of the patient's illness")
#         comorbidities = st.text_input("🦠 Comorbidities (comma-separated)", placeholder="e.g., Arthritis, None", help="Enter any comorbidities separated by commas")
# 
#     st.markdown("---")
# 
#     # Second row for additional details
#     col3, col4 = st.columns(2)
# 
#     with col3:
#         procedure_codes = st.text_input("💉 Procedure Codes (comma-separated)", placeholder="e.g., 4019, 2500", help="Enter the codes for any procedures")
#         ward_department = st.selectbox("🏢 Ward/Department", ['Cardiology', 'Orthopedics', 'Respiratory', 'Transplant', 'General Surgery'], help="Select the department or ward")
# 
#     with col4:
#         discharge_disposition = st.selectbox("🚶 Discharge Disposition", ['Transferred to another facility', 'Long-term Care Facility', 'Home'], help="Select where the patient is discharged to")
# 
#     # Handle missing or empty inputs
#     if not comorbidities:
#         comorbidities = 'None'
#     procedure_codes_count = len(procedure_codes.split(',')) if procedure_codes else 0
# 
#     # Interactive prediction button
#     st.markdown("### When ready, click the button to predict the length of stay")
#     predict_button = st.button('🔍 Predict Length of Stay')
# 
#     if predict_button:
#         data = {
#             'Age': [age],
#             'Gender': [gender],
#             'Admission Type': [admission_type],
#             'Primary Diagnosis': [primary_diagnosis],
#             'Severity of Illness': [severity_of_illness],
#             'Comorbidities': [comorbidities],
#             'Procedure Codes Count': [procedure_codes_count],
#             'Ward/Department': [ward_department],
#             'Discharge Disposition': [discharge_disposition]
#         }
# 
#         input_df = pd.DataFrame(data)
#         predicted_length_of_stay = model_pipeline.predict(input_df)
#         predicted_length_of_stay = np.clip(np.round(predicted_length_of_stay[0]).astype(int), 1, 12)  # Restrict predictions to a maximum of 12 days
# 
#         # Display the predicted length of stay with style
#         st.success(f"🚑 The predicted length of stay is: **{predicted_length_of_stay} days**")
#         st.balloons()
# 
#         # Explain what might happen on each day
#         st.markdown("### Breakdown of Each Day's Procedures")
#         st.info("Here's an overview of what happens during the patient's hospital stay:")
# 
#         for day in range(1, predicted_length_of_stay + 1):
#             st.markdown(f"""
#             <div class="day-box">
#                 <p class="day-title">Day {day}:</p>
#                 <p>{get_day_details(day, predicted_length_of_stay, severity_of_illness)}</p>
#             </div>
#             """, unsafe_allow_html=True)
# 
# def get_day_details(day, predicted_length_of_stay, severity):
#     # Customize details based on the day and severity
#     if severity == 'Mild':
#         if day == 1:
#             return "Basic assessments, diagnostic tests, and initiation of treatment."
#         elif day == 2:
#             return "Continued monitoring with mild interventions if required."
#         elif day <= predicted_length_of_stay - 1:
#             return "Stable condition with basic physiotherapy and continued care."
#         else:
#             return "Final evaluations and discharge preparations."
#     elif severity == 'Moderate':
#         if day == 1:
#             return "Thorough assessments, blood work, and more complex treatments."
#         elif day == 2:
#             return "Ongoing treatment adjustments based on the condition."
#         elif day <= predicted_length_of_stay - 1:
#             return "Additional interventions like imaging or minor surgeries."
#         else:
#             return "Discharge planning and final reviews by the healthcare team."
#     elif severity == 'Severe':
#         if day == 1:
#             return "Critical interventions and monitoring in the ICU."
#         elif day == 2:
#             return "Aggressive treatments or surgeries; patient remains under close observation."
#         elif day <= predicted_length_of_stay - 1:
#             return "Extended ICU care and possible second surgeries or interventions."
#         else:
#             return "Transition to a recovery ward and preparation for discharge."
# 
# if __name__ == '__main__':
#     predict_length_of_stay()
#

#killimng the previous run
!pkill -f streamlit

!choco install ngrok

# authentocation
!ngrok config add-authtoken "2kqawfT6uoasLTlQyAR27wE5qYd_7vNpb4kyfFKm8QsNUq9EW"

from pyngrok import ngrok
import subprocess

# Function to start Streamlit
def start_streamlit():
    subprocess.run(["streamlit", "run", "ok.py"], check=True)

# Function to start ngrok tunnel
def start_ngrok(port):
    ngrok_tunnel = ngrok.connect(port)
    print(f"Streamlit app is live at: {ngrok_tunnel.public_url}")

# Start the ngrok tunnel for port 8501 (default for Streamlit)
port = 8501
start_ngrok(port)

# Run the Streamlit app
start_streamlit()