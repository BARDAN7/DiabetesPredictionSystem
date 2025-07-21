from django.shortcuts import render, redirect
import joblib
import numpy as np
import os

# Get BASE_DIR for model path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, 'diabetes_predictor', 'Diabetes_Predictor.joblib')

# Load the trained model
model = joblib.load(model_path)
def home(request):
    return render(request, 'diabetes_predictor/index.html')

def predict(request):
    if request.method == 'POST':
        try:
            age = float(request.POST['age'])
            gender = request.POST['gender']
            hypertension = int(request.POST['hypertension'])
            heart_disease = int(request.POST['heart_disease'])
            smoking_history = request.POST['smoking_history']
            bmi = float(request.POST['bmi'])
            hba1c = float(request.POST['hba1c_level'])
            glucose = float(request.POST['blood_glucose_level'])

            # Encode gender
            gender_map = {'male': 1, 'female': 0, 'other': 2}
            gender_num = gender_map.get(gender.lower(), 2)

            # Encode smoking history
            smoking_map = {
                'current': 0,
                'ever': 1,
                'former':2,
                'never': 3,
                'no info':4,
                'not current': 5
            }
            smoking_num = smoking_map.get(smoking_history.lower(), 1)
            features = np.array([[age, gender_num, hypertension, heart_disease, smoking_num, bmi, hba1c, glucose]])
            prediction = model.predict(features)[0]

            result_param = 'positive' if prediction == 1 else 'negative'

            # Redirect with result
            return redirect(f'/result/?result={result_param}')

        except Exception as e:
            return render(request, 'diabetes_predictor/index.html', {'error': str(e)})
    else:
        return render(request, 'diabetes_predictor/index.html')

def result(request):
    return render(request, 'diabetes_predictor/result.html')
