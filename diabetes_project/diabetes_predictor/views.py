from django.shortcuts import render, redirect
import joblib
import numpy as np
import os
from .models import DiabetesHistory
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm
from django.contrib.auth import login
from django.contrib.auth import logout
from .models import DiabetesHistory, Profile

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
                'former': 2,
                'never': 3,
                'no info': 4,
                'not current': 5
            }
            smoking_num = smoking_map.get(smoking_history.lower(), 1)

            # Prepare features and make prediction
            features = np.array([[age, gender_num, hypertension, heart_disease, smoking_num, bmi, hba1c, glucose]])
            prediction = model.predict(features)[0]

            # Determine result
            result_param = 'positive' if prediction == 1 else 'negative'

            # Medicine recommendation logic
            if glucose < 100 and hba1c < 5.7:
                result_text = "Normal"
                medicine = (
                    "No medicine required. Maintain a balanced diet, regular exercise, "
                    "and a healthy lifestyle to prevent diabetes."
                )

            elif 100 <= glucose < 126 or 5.7 <= hba1c < 6.5:
                result_text = "Pre-Diabetic"
                medicine = (
                    "Metformin 500mg once daily (consult your doctor before starting). "
                    "Focus on diet control, weight loss, and physical activity to prevent diabetes progression."
                )

            else:
                result_text = "Diabetic"
                if glucose >= 250 or hba1c >= 9:
                    medicine = (
                        "Insulin therapy may be required. Please consult your endocrinologist for proper dosage. "
                        "Maintain regular blood sugar monitoring and follow a diabetic-friendly meal plan."
                    )
                else:
                    medicine = (
                        "Metformin 500mg twice daily after meals. "
                        "If blood sugar remains uncontrolled, your doctor may prescribe additional medication "
                        "or start you on insulin therapy. Always follow medical supervision."
                    )

            # Save prediction result in database
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
                result=result_text,
                medicine=medicine
            )

            # Pass data to result page
            return render(
                request,
                'diabetes_predictor/result.html',
                {
                    'result': result_text,
                    'medicine': medicine,
                    'age': age,
                    'gender': gender,
                    'bmi': bmi,
                    'hba1c': hba1c,
                    'glucose': glucose
                }
            )

        except Exception as e:
            return render(request, 'diabetes_predictor/index.html', {'error': str(e)})

    return render(request, 'diabetes_predictor/index.html')



from django.shortcuts import render

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = Profile.objects.get(user=user)
            profile.phone = form.cleaned_data.get('phone')
            profile.save()
            # request.session['phone'] = phone  # Save temporarily in session
            login(request, user)
            return redirect("login")  # redirect to login page
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

@login_required
def home(request):
    return render(request, 'diabetes_predictor/home.html')

@login_required
def contact(request):
    return render(request, 'diabetes_predictor/contact.html')

@login_required
def print_result(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    try:
        profile = user.profile
        phone = profile.phone
    except:
        phone = "N/A"

    # Fetch the latest prediction record of the user
    latest_record = DiabetesHistory.objects.filter(user=user).last()

    if not latest_record:
        return redirect('predict')  # redirect if no record found

    context = {
        'record': latest_record,
        'user': request.user,
        'profile': profile
    }

    return render(request, 'diabetes_predictor/print_result.html', context)

def logout_view(request):
    logout(request)
    return redirect("login")