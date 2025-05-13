from flask import Flask, render_template, request, redirect, flash,session,url_for,jsonify
from flask_mysqldb import MySQL
import re
import os
import joblib
import io
from reportlab.pdfgen import canvas
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import pickle
import numpy as np
import pandas as pd
from datetime import timedelta
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import dotenv
from fpdf import FPDF
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


dotenv.load_dotenv()

app = Flask(__name__)
app.secret_key = "group10"
app.permanent_session_lifetime = timedelta(minutes=50)

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False


mail = Mail(app)
serializer = URLSafeTimedSerializer(app.secret_key)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # Change to your MySQL password
app.config['MYSQL_DB'] = 'healthcheck'
#app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# File Upload Configuration
UPLOAD_FOLDER = "static/profile_pics"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Load the trained model
heart_model = pickle.load(open('heart_disease_model.sav', 'rb'))
diabetes_model = pickle.load(open('diabetes_model.sav', 'rb')) 
kidney_model =  pickle.load(open('kidney_disease(short).sav', 'rb'))
Breast_Cancer_model = pickle.load(open('Breast_Cancer.sav', 'rb'))
Liver_model = pickle.load(open('liver_model.sav', 'rb'))
Liver_scaler_model = pickle.load(open('liver_scaler.sav', 'rb'))
model_package = joblib.load('parkinsons_model_package.sav')
model = model_package['model']
scaler = model_package['scaler']
selected_features = model_package['features']

with open("disease_predictor.pkl", "rb") as f:
    model = pickle.load(f)

with open("symptom_list.pkl", "rb") as f:
    symptom_list = pickle.load(f)

with open("disease_names.pkl", "rb") as f:
    disease_mapping = pickle.load(f)

# Email & Password Validation
def validate_email(email):
    return re.match(r"^[a-zA-Z0-9._%+-]+@gmail\.com$", email)

def validate_password(password):
    return re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password)

# Phone Number Validation
def validate_phone(phone):
    return re.match(r"^[6-9]\d{9}$", phone)  # Starts with 6-9 and has exactly 10 digits

# Username Validation
def validate_username(username):
    return re.match(r"^[A-Za-z][A-Za-z0-9_]{2,19}$", username)

#Home Route
@app.route('/')
def home():
    return render_template('home.html')

# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form["username"]
        email = request.form['email']
        phone = request.form['phone']
        gender = request.form['gender']
        password = request.form['password']

        if not validate_username(username):
            flash("Username must start with a letter, be 3–20 characters long, and contain only letters, numbers, or underscores.", "danger")
            return redirect('/signup')

        if not validate_email(email):
            flash("Email must be a valid Gmail address (example@gmail.com)", "danger")
            return redirect('/signup')

        if not validate_password(password):
            flash("Password must be at least 8 characters long, containing at least one uppercase letter, one lowercase letter, one number, and one special character.", "danger")
            return redirect('/signup')
        
        if not validate_phone(phone):
            flash("Phone number must be 10 digits and start with 6, 7, 8, or 9.", "danger")
            return redirect('/signup')

        hashed_password = generate_password_hash(password)
        cur = mysql.connection.cursor()
         # Check for duplicate username
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            flash("Username already taken. Please choose a different one.", "danger")
            cur.close()
            return redirect('/signup')

        # Check for duplicate password
        cur.execute("SELECT * FROM users WHERE password = %s", (password,))
        if cur.fetchone():
            flash("This password is already in use. Please choose a different one for better security.", "danger")
            cur.close()
            return redirect('/signup')
        
        # Handle Profile Picture Upload
        file = request.files["profile_pic"]
        filename = "default.png"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

        
        try:
            cur.execute("INSERT INTO users (username,email, phone, gender, password,profile_pic) VALUES (%s, %s, %s, %s,%s,%s)", 
                        (username,email, phone, gender, hashed_password,filename))
            mysql.connection.commit()
            flash("Account created successfully! Please log in.", "success")
            return redirect('/login')
        except:
            flash("Email already exists. Please use a different email.", "danger")
            return redirect('/signup')
        finally:
            cur.close()

    return render_template('signup.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = request.form.get('remember')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        print(user)
        cur.close()

        if user and check_password_hash(user[5], password):  # user[5] is the password column
        #if user and check_password_hash(user['password'], password):

            session['logged_in'] = True
            #session['email'] = user[2]
            session['id'] = user[0]
            session['username']=user[1]
            session['email'] = user[2]
            session['email'] = email
            print(session['email'])
            session['profile_pic'] = user[6]
            session['phone'] = user[3]
            session['gender'] = user[4]

            if remember:
                session.permanent = True
                app.permanent_session_lifetime = timedelta(days=30)
            else:
                session.permanent = False

            flash("Login successful!", "success")
            return render_template('dashboard.html')

        else:
            flash("Invalid email or password. Please try again.", "danger")
            return redirect('/login')

    return render_template('login.html')

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect('/')

# Route for Forgot Password Page
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email'].strip()

        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email format", "danger")
            return redirect(url_for('forgot_password'))

        # Check if email exists in DB
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user:
            # Generate token
            token = serializer.dumps(email, salt='password-reset-salt')
            reset_url = url_for('reset_password_token', token=token, _external=True)

            # Send email
            msg = Message("Reset Your HealthCheck Password", sender=os.environ.get('MAIL_USERNAME'), recipients=[email])
            msg.body = f"Hi, click the link below to reset your password:\n\n{reset_url}\n\nThis link is valid for 10 minutes."
            mail.send(msg)

            flash("A password reset link has been sent to your email.", "info")
            return redirect(url_for('login'))
        else:
            flash("Email not found in our records", "danger")
            return redirect(url_for('forgot_password'))

    return render_template('forgot_password.html')


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password_token(token):
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=600)  # 10 minutes validity
    except Exception as e:
        flash("The reset link is invalid or has expired.", "danger")
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if not new_password or new_password != confirm_password:
            flash("Passwords do not match or are empty", "danger")
            return redirect(url_for('reset_password_token', token=token))

        hashed_password = generate_password_hash(new_password)
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
        mysql.connection.commit()
        cur.close()

        flash("Your password has been updated. Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('reset_password_form.html', token=token)

#Symptoms Route
@app.route('/get_symptoms')
def get_symptoms():
    return jsonify({'symptoms': symptom_list})

@app.route('/predict_disease_symptoms', methods=['GET', 'POST'])
def predict_disease():
    if request.method == 'GET':
        return render_template('disease_prediction.html')

    data = request.get_json()
    selected_symptoms = data.get('symptoms', [])

    if not selected_symptoms:
        return jsonify({'error': 'No symptoms selected'}), 400

    # Create a binary vector of symptoms
    input_vector = [1 if symptom in selected_symptoms else 0 for symptom in symptom_list]

    # Predict probabilities
    probabilities = model.predict_proba([input_vector])[0]
    top_indices = sorted(range(len(probabilities)), key=lambda i: probabilities[i], reverse=True)[:3]

    results = []
    for idx in top_indices:
        disease = disease_mapping[idx]
        probability = round(probabilities[idx] * 100, 2)
        results.append({'disease': disease, 'probability': probability})

    return jsonify({'results': results})



# About Route
@app.route('/about')
def about():
    return render_template('about.html')

# Dashboard (Protected Route)
@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        flash("Please log in first.", "warning")
        return redirect('/login')
        
    return render_template('dashboard.html')


@app.route('/heart_prediction', methods=['GET', 'POST'])
def heart_prediction():
    if request.method == 'POST':
        try:
            # Extract input values safely using request.form.get()
            input_data = [
                float(request.form.get('age', 0)),
                float(request.form.get('sex', 0)),
                float(request.form.get('cp', 0)),
                float(request.form.get('trestbps', 0)),
                float(request.form.get('chol', 0)),
                float(request.form.get('fbs', 0)),
                float(request.form.get('restecg', 0)),
                float(request.form.get('thalach', 0)),
                float(request.form.get('exang', 0)),
                float(request.form.get('oldpeak', 0)),
                float(request.form.get('slope', 0)),
                float(request.form.get('ca', 0)),
                float(request.form.get('thal', 0))
            ]

            # Convert into numpy array for model prediction
            input_array = np.array(input_data).reshape(1, -1)

            # Predict using the model
            prediction = heart_model.predict(input_array)[0]

            # Result message
            result_text = "Heart Disease Detected (Positive)" if prediction == 1 else "No Heart Disease (Negative)"

            # Medicine advice if prediction is positive
            if prediction == 1:
                advice = (
                    "Suggested actions:\n"
                    "- Aspirin (blood thinner)\n"
                    "- Beta-blockers (e.g., Metoprolol)\n"
                    "- Statins (e.g., Atorvastatin for cholesterol)\n"
                    "- ACE inhibitors (e.g., Ramipril)\n"
                    "- Lifestyle: quit smoking, reduce salt intake, exercise regularly"
                )
            else:
                advice = "Keep maintaining a healthy lifestyle — regular exercise, healthy diet, avoid smoking."

            return jsonify({
                "success": True,
                "prediction": result_text,
                "advice": advice
            })

        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    return render_template('heart_prediction.html')

@app.route("/save_pdf", methods=["POST"])
def save_pdf():
    try:
        if 'username' not in session:
            return jsonify({"success": False, "error": "User not logged in"})

        if 'pdf' not in request.files:
            return jsonify({"success": False, "error": "No PDF uploaded"})

        # Get data from request
        pdf_file = request.files['pdf']
        prediction_result = request.form.get("prediction_result", "Unknown")
        disease_name = request.form.get("disease_name", "Unknown_Disease")  # Generic disease name
        username = session['username']

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        sanitized_disease = disease_name.lower().replace(" ", "_")
        filename = f"{username}_{sanitized_disease}_report_{timestamp}.pdf"
        save_path = os.path.join("static/reports", filename)

        # Save PDF to directory
        os.makedirs("static/reports", exist_ok=True)
        pdf_file.save(save_path)

        # Save entry to database
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO user_activity (username, disease_name, prediction_result, pdf_report)
            VALUES (%s, %s, %s, %s)
        """, (
            username,
            disease_name,
            prediction_result,
            save_path
        ))
        mysql.connection.commit()
        cursor.close()

        return jsonify({"success": True, "pdf_report_url": "/" + save_path})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/activity')
def user_activity():
    # Get the user ID from session (assuming it's stored in session)
    username = session.get('username')
    
    if username is None:
        # Handle if the user is not logged in
        return redirect(url_for('login'))

    # Query the user_activity table
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM user_activity WHERE username = %s ORDER BY created_at DESC", (username,))
    activities = cursor.fetchall()
    cursor.close()

    # Render the template with the fetched activities
    return render_template('activity.html', activities=activities)

@app.route('/diabetes', methods=['GET', 'POST'])
def diabetes():
    if request.method == 'POST':
        try:
            # Extract form values and convert them into float
            input_data = [float(request.form[key]) for key in ['pregnancies', 'glucose', 'bloodPressure', 
                                                               'skinThickness', 'insulin', 'bmi', 
                                                               'diabetesPedigree', 'age']]
            # Convert into numpy array for model prediction
            input_array = np.array(input_data).reshape(1, -1)

            # Predict using model
            prediction = diabetes_model.predict(input_array)[0]

            # Determine result
            result_text = "Diabetes Detected (Positive)" if prediction == 1 else "No Diabetes (Negative)"

            return jsonify({"success": True, "prediction": result_text})

        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    return render_template('diabetes.html')



@app.route('/parkinson', methods=['GET', 'POST'])
def parkinson():
    result = None
    suggestion = None
    if request.method == 'POST':
        try:
            # Get input values from the form
            input_values = [float(request.form[feature]) for feature in selected_features]


            # Create DataFrame
            input_df = pd.DataFrame([input_values], columns=selected_features)

            # Scale and predict
            input_scaled = scaler.transform(input_df)
            prediction = model.predict(input_scaled)[0]

            # Generate result and suggestion
            if prediction == 1:
                result = "Parkinson's Detected 😔"
                suggestion = (
                    "Please consult a neurologist for a detailed diagnosis. "
                    "Engaging in physical therapy, voice exercises, a healthy diet, and regular follow-ups "
                    "can help manage symptoms effectively. Joining a support group is also highly beneficial."
                )
            else:
                result = "Healthy 🙂"

        except Exception as e:
            result = f"Error occurred: {e}"
    return render_template('parkinson.html', features=selected_features, result=result)
          # Create DataFrame
          #input_df = pd.DataFrame([input_values], columns=selected_features)

            # Scale and predict
            #input_scaled = scaler.transform(input_df)
            #prediction = model.predict(input_scaled)[0]

            # Generate result
            #result = "Parkinson's Detected 😔" if prediction == 1 else "Healthy 🙂"

        #except Exception as e:
            #result = f"Error occurred: {e}"

    #return render_template('parkinson.html', features=selected_features, result=result)
    return render_template('parkinson.html', features=selected_features, result=result, suggestion=suggestion)


@app.route('/Breast_cancer', methods=['GET', 'POST'])
def Breast_cancer():
    if request.method == 'POST':
        try:
            # Extract form values and convert them into float
            input_data = [float(request.form[key]) for key in [
                                                            'radius_mean', 'texture_mean', 'perimeter_mean', 'area_mean', 'smoothness_mean',
                                                            'compactness_mean', 'concavity_mean', 'concave points_mean', 'symmetry_mean', 'fractal_dimension_mean'
                                                            #'radius_se ', 'texture_se', 'perimeter_se', 'area_se', 'smoothness_se',
                                                            #'compactness_se', 'concavity_se', 'concave points_se', 'symmetry_se', 'fractal_dimension_se',
                                                            #'radius_worst', 'texture_worst', 'perimeter_worst', 'area_worst', 'smoothness_worst',
                                                            #'compactness_worst', 'concavity_worst', 'concave points_worst', 'symmetry_worst', 'fractal_dimension_worst'
                                                            ]]
            # Convert into numpy array for model prediction
            input_array = np.array(input_data).reshape(1, -1)

            # Predict using model
            prediction = Breast_Cancer_model.predict(input_array)[0]

            # Determine result
            result_text = "The Breast Cancer is Benign" if prediction == 0 else "The Breast cancer is Malignant"

            return jsonify({"success": True, "prediction": result_text})

        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    return render_template('Breast_cancer.html')

@app.route('/liver', methods=['GET', 'POST'])
def liver():
    if request.method == 'POST':
        try:
            # Extract form values and convert them into float
            input_data = [float(request.form[key]) for key in [
                                                                    'Age',
                                                                    'Gender',
                                                                    'Total_Bilirubin',
                                                                    'Direct_Bilirubin',
                                                                    'Alkaline_Phosphotase',
                                                                    'Alamine_Aminotransferase',
                                                                    'Aspartate_Aminotransferase',
                                                                    'Total_Protiens',
                                                                    'Albumin',
                                                                    'Albumin_and_Globulin_Ratio'
                                                                ]]
            #input_array = np.array(input_data).reshape(1, -1)
            input_scaled = Liver_scaler_model.transform([input_data])

            # Predict using model
            prediction = Liver_model.predict(input_scaled)

            # Determine result
            result_text = "The prediction indicates a positive case of liver disease." if prediction == 1 else "You are predicted safe from liver disease (Negative)"

            return jsonify({"success": True, "prediction": result_text})

        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    return render_template('liver.html')



@app.route('/kidney', methods=['GET', 'POST'])
def kidney():
    if request.method == 'POST':
        try:
            # Extract form values and convert them into float

            
            # input_data = [request.form[key] for key in [ 'Age', 'Blood Pressure', 'Specific gravity (Urine cocentration)', 'Albumin',
            #                                             'Blood Sugar', 'Red Blood cells in Urine', 'Pus Cells in urine',
            #                                             'Pus Cell Clumps in Urine', 'Bacteria in Urine', 'Blood Glucose',
            #                                             'Blood Urea(mg/dL)', 'Serum Creatinine(mg/dL)', 'Sodium', 'Potassium', 'Hemoglobin(g/dl)',
            #                                             'Packed Cell Volume(%)', 'White Blood Cell Count (/cubic mm)',
            #                                             'Red Blood Cell Count (million/cumm)', 'Hypertension', 'Diabetes',
            #                                             'Coronary Artery Disease', 'Appetite', 'Pedal Edema (swelling in leg/feet)',
            #                                             'Anemia']]

            input_data = [request.form[key] for key in ["Age", "Blood Pressure", "Specific gravity (Urine cocentration)", "Albumin", "Red Blood cells in Urine", "Blood Urea(mg/dL)", "Serum Creatinine(mg/dL)", "Hemoglobin(g/dl)", "Packed Cell Volume(%)", "Hypertension", "Diabetes"]]
            
            # Convert into numpy array for model prediction
            input_array = np.array(input_data).reshape(1, -1)

            # Predict using model
            prediction = kidney_model.predict(input_array)[0]

            # Determine result
            result_text = "The prediction indicates a positive case of chronic kidney disease." if prediction == 0 else "You are predicted safe from Chronic Kidney disease (Negative)"

            # return jsonify({"success": True, "prediction": result_text})
            return jsonify({"success": True, "prediction": result_text, "result": int(prediction)})

        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    return render_template('kidney.html')


@app.route("/BMI")
def bmi():
    return render_template("BMI.html")

@app.route("/BMR")
def bmr():
    return render_template("BMR.html")


@app.route('/profile')
def profile():
    if 'email' not in session:
        return redirect('/login')
    return render_template('profile.html')


@app.route('/profile-data')
def profile_data():
    if 'email' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    cur = mysql.connection.cursor()
    cur.execute("SELECT username,email, phone, gender, profile_pic FROM users WHERE email = %s", (session['email'],))
    user = cur.fetchone()
    cur.close()


    if user:
        return jsonify({
            "username": user[0],
            "email": user[1],
            "phone": user[2],
            "gender": user[3],
            "profile_pic": user[4] if user[4] else "/static/profile_pics/default.png"  # Handle missing images
        })
    else:
        return jsonify({"error": "User not found"}), 404


    

@app.route('/edit-profile')
def edit_profile():
    if 'email' not in session:
        return redirect('/login')
    return render_template('edit.html')

@app.route('/update-profile', methods=['POST'])
def update_profile():
    if 'email' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    username = request.form['username']
    #email = request.form['email']
    phone = request.form['phone']
    #gender = request.form['gender']

    profile_pic = None
    if 'profile_pic' in request.files:
        file = request.files['profile_pic']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            profile_pic = filename

    cur = mysql.connection.cursor()

    if profile_pic:
        cur.execute("UPDATE users SET username=%s,phone=%s,profile_pic=%s WHERE email=%s",
                    (username, phone,profile_pic, session['email']))
    else:
        cur.execute("UPDATE users SET username=%s, phone=%s WHERE email=%s",
                    (username, phone,session['email']))

    mysql.connection.commit()
    cur.close()

    return jsonify({"success": True, "message": "Profile updated successfully!"})

@app.route("/save_health_result", methods=["POST"])
def save_health_result():
    if 'username' not in session:
        flash("You must be logged in to save your result.", "danger")
        return redirect(url_for('login'))

    username = session['username']
    height = request.form.get("height")
    weight = request.form.get("weight")
    result_type = request.form.get("category")  # Either 'BMI' or 'BMR'
    result_value = request.form.get("result_value")  # BMI/BMR number
    pdf_file = request.files.get("pdf")

    if not all([height, weight, result_type, result_value, pdf_file]):
        return "Missing form data", 400

    # Save PDF file securely
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = secure_filename(f"{username}_{result_type}_{timestamp}.pdf")
    pdf_path = os.path.join("static/pdfs", filename)

    # Save PDF to directory
    os.makedirs("static/pdfs", exist_ok=True)
    pdf_file.save(pdf_path)
    

    # Save to database
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO health_reports (username, height, weight, category, result_value, pdf_path, created_at) VALUES (%s, %s, %s, %s, %s, %s, NOW())",
        (username, height, weight, result_type, result_value, pdf_path)
    )
    mysql.connection.commit()
    cur.close()

    return "✅ Report saved successfully", 200

@app.route('/healthactivity')
def health_activity():
    # Get the user ID from session (assuming it's stored in session)
    username = session.get('username')
    
    if username is None:
        # Handle if the user is not logged in
        return redirect(url_for('login'))

    # Query the user_activity table
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM health_reports WHERE username = %s ORDER BY created_at DESC", (username,))
    activities = cursor.fetchall()
    cursor.close()

    # Render the template with the fetched activities
    return render_template('bmi_bmr_activity.html', activities=activities)


if __name__ == '__main__':
    app.secret_key = "group10"
    app.run(debug=True)


