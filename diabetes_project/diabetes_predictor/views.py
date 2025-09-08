from django.shortcuts import render, redirect
import joblib
import numpy as np
import os
from .models import DiabetesHistory
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm

# Get BASE_DIR for model path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, 'diabetes_predictor', 'Diabetes_Predictor.joblib')

# Load the trained model
model = joblib.load(model_path)
def home(request):
    return render(request, 'diabetes_predictor/index.html')
@login_required(login_url='login')
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

            # Save to database
            DiabetesHistory.objects.create(
                user=request.user,
                age=age,
                gender=gender,
                hypertension=bool(hypertension),
                heart_disease=bool(heart_disease),
                smoking_history=smoking_history,
                bmi=bmi,
                hba1c_level=hba1c,
                blood_glucose_level=glucose,
                result=result_param
            )

            return redirect(f'/result/?result={result_param}')

        except Exception as e:
            return render(request, 'diabetes_predictor/index.html', {'error': str(e)})

    return render(request, 'diabetes_predictor/index.html')


from django.shortcuts import render

from django.shortcuts import render

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect("login")
        else:
            print(form.errors)  # 🔥 This will print why signup failed
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


def index(request):
    return render(request, 'diabetes_predictor/index.html')
@login_required(login_url='login')
def history(request):
    records = DiabetesHistory.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'diabetes_predictor/history.html', {'records': records})
from django.shortcuts import render

def result(request):
    return render(request, 'diabetes_predictor/result.html')


@login_required(login_url='login')
def delete_record(request, id):
    record = get_object_or_404(DiabetesHistory, id=id, user=request.user)
    record.delete()
    return redirect('history')
