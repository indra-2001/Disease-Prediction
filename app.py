from flask import Flask, render_template, request, redirect, flash,session,url_for,jsonify
from flask_mysqldb import MySQL
import re
import os
import joblib
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

import joblib
# import pandas as pd
from datetime import timedelta
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import dotenv

import warnings
warnings.filterwarnings('ignore')


dotenv.load_dotenv()

app = Flask(__name__)
app.secret_key = "group10"
app.permanent_session_lifetime = timedelta(minutes=5)

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


# Email & Password Validation
def validate_email(email):
    return re.match(r"^[a-zA-Z0-9._%+-]+@gmail\.com$", email)

def validate_password(password):
    return re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password)

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

        if not validate_email(email):
            flash("Email must be a valid Gmail address (example@gmail.com)", "danger")
            return redirect('/signup')

        if not validate_password(password):
            flash("Password must be at least 8 characters long, containing at least one uppercase letter, one lowercase letter, one number, and one special character.", "danger")
            return redirect('/signup')

        hashed_password = generate_password_hash(password)

         # Handle Profile Picture Upload
        file = request.files["profile_pic"]
        filename = "default.png"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO users (username,email, phone, gender, password,profile_pic) VALUES (%s, %s, %s, %s,%s,%s)", 
                        (username,email, phone, gender, hashed_password,filename))
            mysql.connection.commit()
            flash("Signup successful! Please login.", "success")
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
        print(email)
        password = request.form['password']
        remember = request.form.get('remember')

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[5], password):  # user[5] is the password column
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

            # advices according to condition
            if prediction == 1:
                decission = "🔴 Heart Disease Detected (Positive)";
                advice = """
<p>Your test suggests signs of heart disease. Early intervention through medication, lifestyle changes, and regular monitoring is essential to reduce risk and improve quality of life.</p>

<h5 class="mt-4 fw-bold text-danger"><i class="bi bi-activity text-primary fs-3 me-2"></i>Advices to Manage Your Condition ----</h5>

<h6 class="mt-3" style="color:#d63384;"><i class="bi bi-capsule-pill me-2"></i>Medications:</h6>
<ul class="ms-3">
    <li>Do not stop medications without consulting your doctor.</li>
    <li>Take prescribed medicines on time (e.g., beta-blockers, statins, aspirin, ACE inhibitors).</li>
    <li>Avoid over-the-counter NSAIDs like ibuprofen unless approved by your cardiologist.</li>
    <li>Inform your doctor about all supplements or herbal products you're using.</li>
</ul>

<h6 class="mt-3" style="color:#20c997;"><i class="bi bi-egg-fried me-2"></i>Diet & Nutrition:</h6>
<ul class="ms-3">
    <li>Eat more fruits, vegetables, whole grains, and lean proteins.</li>
    <li>Reduce salt intake to lower blood pressure.</li>
    <li>Avoid saturated fats and trans fats — limit red meat, butter, and fried foods.</li>
    <li>Cut back on sugar and processed foods to manage weight and blood sugar.</li>
</ul>

<h6 class="mt-3" style="color:#fd7e14;"><i class="bi bi-person-walking me-2"></i>Lifestyle:</h6>
<ul class="ms-3">
    <li>Quit smoking — it significantly worsens heart and blood vessel health.</li>
    <li>Exercise regularly (e.g., brisk walking 30 minutes a day, 5 days a week).</li>
    <li>Maintain a healthy weight and BMI.</li>
    <li>Limit alcohol — excess drinking raises blood pressure and heart risk.</li>
    <li>Sleep 7–8 hours daily and manage stress with relaxation techniques like yoga or meditation.</li>
</ul>

<h6 class="mt-3" style="color:#0d6efd;"><i class="bi bi-heart-pulse me-2"></i>Monitor Your Health:</h6>
<ul class="ms-3">
    <li>Check blood pressure and cholesterol levels regularly.</li>
    <li>Monitor heart rate and report irregular beats or chest discomfort.</li>
    <li>Keep diabetes under control if present.</li>
    <li>Attend regular follow-ups and screenings (e.g., ECG, echocardiogram if advised).</li>
</ul>

<h6 class="mt-3" style="color:#dc3545;"><i class="bi bi-exclamation-triangle-fill me-2"></i>Seek Medical Help If:</h6>
<ul class="ms-3">
    <li>You feel chest pain, tightness, or pressure.</li>
    <li>You experience sudden fatigue, breathlessness, or dizziness.</li>
    <li>You notice swelling in legs, ankles, or sudden weight gain.</li>
    <li>Your symptoms worsen or new ones appear.</li>
</ul>

<p class="mt-3"><strong>Note:</strong> Always follow up with your cardiologist for a tailored treatment plan.</p>
            """

            else:
                decission = "🟢 No Heart Disease Detected (Negative)";        
                advice = """
<p>Great news! Your test results do not show signs of heart disease. But staying heart-healthy is a lifelong effort.</p>

<h5 class="mt-4 fw-bold text-success"><i class="bi bi-heart-pulse text-primary fs-4 me-2 align-middle"></i>Continue with These Practices to Maintain Your Heart Health ----</h5>

<h6 class="mt-3" style="color:#20c997;"><i class="bi bi-egg-fried me-2"></i>Diet & Nutrition:</h6>
<ul class="ms-3">
    <li>Follow a Mediterranean-style diet: rich in vegetables, fruits, whole grains, and lean proteins.</li>
    <li>Avoid processed, sugary, and fatty foods.</li>
    <li>Use healthy fats like olive oil instead of butter or margarine.</li>
    <li>Reduce salt to help keep blood pressure in check.</li>
</ul>

<h6 class="mt-3" style="color:#fd7e14;"><i class="bi bi-person-walking me-2"></i>Lifestyle:</h6>
<ul class="ms-3">
    <li>Be physically active at least 150 minutes a week (e.g., brisk walking, cycling).</li>
    <li>Avoid tobacco in all forms — it damages your heart and blood vessels.</li>
    <li>Limit alcohol consumption.</li>
    <li>Maintain a healthy weight and sleep 7–8 hours nightly.</li>
    <li>Practice stress reduction techniques such as yoga, meditation, or deep breathing.</li>
</ul>

<h6 class="mt-3" style="color:#0d6efd;"><i class="bi bi-clipboard-pulse me-2"></i>Monitor Regularly:</h6>
<ul class="ms-3">
    <li>Get your blood pressure, cholesterol, and glucose levels checked routinely.</li>
    <li>If you have a family history of heart disease, keep up with screenings.</li>
</ul>

<p class="mt-3 fw-semibold">Keep in touch with your healthcare provider for periodic evaluations.</p>
<p><strong>A healthy lifestyle today means a healthier heart tomorrow!</strong></p>
            """


            return jsonify({
                "success": True,
                "prediction": result_text,
                "advice": advice,
                "decission": decission
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
# @app.route('/heart_prediction', methods=['GET', 'POST'])
# def heart_prediction():
#     if request.method == 'POST':
#         try:
#             # if 'user_id' not in session or 'username' not in session:
#             #     return jsonify({"success": False, "error": "User not logged in"})

#             # Extract input values
#             input_data = [
#                 float(request.form.get('age', 0)),
#                 float(request.form.get('sex', 0)),
#                 float(request.form.get('cp', 0)),
#                 float(request.form.get('trestbps', 0)),
#                 float(request.form.get('chol', 0)),
#                 float(request.form.get('fbs', 0)),
#                 float(request.form.get('restecg', 0)),
#                 float(request.form.get('thalach', 0)),
#                 float(request.form.get('exang', 0)),
#                 float(request.form.get('oldpeak', 0)),
#                 float(request.form.get('slope', 0)),
#                 float(request.form.get('ca', 0)),
#                 float(request.form.get('thal', 0))
#             ]

#             input_array = np.array(input_data).reshape(1, -1)
#             prediction = heart_model.predict(input_array)[0]
#             result_text = "Heart Disease Detected (Positive)" if prediction == 1 else "No Heart Disease (Negative)"

#             if prediction == 1:
#                 advice = (
#                     "Suggested actions:\n"
#                     "- Aspirin (blood thinner)\n"
#                     "- Beta-blockers (e.g., Metoprolol)\n"
#                     "- Statins (e.g., Atorvastatin)\n"
#                     "- ACE inhibitors (e.g., Ramipril)\n"
#                     "- Lifestyle: quit smoking, reduce salt intake, exercise regularly"
#                 )
#             else:
#                 advice = "Keep maintaining a healthy lifestyle — regular exercise, healthy diet, avoid smoking."

#             # PDF generation
#             if 'email' in session:
#                 print("email is:", session['email'])  
#             else:
#                 print("No email found in session")
#             username = session['username']
#             print(username)
#             timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
#             filename = f"{username}_heart_report_{timestamp}.pdf"
#             pdf_path = os.path.join("static/reports", filename)

#             pdf = FPDF()
#             pdf.add_page()
#             pdf.set_font("Arial", size=12)
#             pdf.cell(200, 10, txt="Heart Disease Prediction Report", ln=True, align="C")
#             pdf.ln(10)
#             pdf.cell(200, 10, txt=f"Username: {username}", ln=True)
#             pdf.cell(200, 10, txt=f"Disease: Heart Disease", ln=True)
#             pdf.cell(200, 10, txt=f"Prediction: {result_text}", ln=True)
#             pdf.ln(10)
#             pdf.multi_cell(0, 10, txt=f"Advice:\n{advice}")

#             os.makedirs("static/reports", exist_ok=True)
#             pdf.output(pdf_path)
#             print(pdf_path)

#             # Save activity to DB
#             cursor = mysql.connection.cursor()
#             cursor.execute("""
#                 INSERT INTO user_activity (username, disease_name, prediction_result, pdf_report)
#                 VALUES (%s, %s, %s, %s)
#             """, (
#                 username,
#                 "Heart Disease",
#                 result_text,
#                 pdf_path
#             ))
#             mysql.connection.commit()
#             cursor.close()

#             return jsonify({
#                 "success": True,
#                 "prediction": result_text,
#                 "advice": advice,
#                 "pdf_report_url": "/" + pdf_path
#             })

#         except Exception as e:
#             return jsonify({"success": False, "error": str(e)})

#     return render_template('heart_prediction.html')

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
            
            # advices according to condition
            if prediction == 1:
                decission = "🔴 Diabetes Detected (Positive)";
                advice = """
<p>Your test indicates signs of Diabetes. Managing blood sugar levels through diet, exercise, medication, and monitoring is crucial to prevent complications and maintain a healthy life.</p>

<h5 class="mt-4 fw-bold text-danger"><i class="bi bi-graph-up-arrow text-primary fs-3 me-2"></i>Advices to Manage Your Condition ----</h5>

<h6 style="color: #1E90FF; margin-top: 20px;"><i class="bi bi-capsule me-2"></i>Medications</h6>
<ul>
  <li>Take your diabetes medications exactly as prescribed.</li>
  <li>Do not skip doses and never change dosages without consulting your doctor.</li>
  <li>If using insulin, store it properly and learn correct injection techniques.</li>
  <li>Discuss all supplements or herbal remedies with your healthcare provider before using them.</li>
</ul>

<h6 style="color: #d35400; margin-top: 20px;"><i class="bi bi-egg-fried me-2"></i>Diet & Nutrition</h6>
<ul>
  <li>Focus on whole grains, fresh vegetables, lean proteins, and healthy fats.</li>
  <li>Limit sugary foods, sweetened drinks, and processed snacks.</li>
  <li>Watch carbohydrate intake and follow a consistent meal plan.</li>
  <li>Reduce sodium to help control blood pressure.</li>
</ul>

<h6 style="color: #27ae60; margin-top: 20px;"><i class="bi bi-heart-pulse me-2"></i>Lifestyle</h6>
<ul>
  <li>Engage in at least 30 minutes of physical activity most days of the week.</li>
  <li>Quit smoking — it raises your risk of complications.</li>
  <li>Limit alcohol intake; it can affect blood sugar levels.</li>
  <li>Maintain a healthy weight and aim for steady, gradual weight loss if overweight.</li>
  <li>Get enough restful sleep and manage stress effectively.</li>
</ul>

<h6 style="color: #8e44ad; margin-top: 20px;"><i class="bi bi-clipboard2-pulse me-2"></i>Monitor Your Health</h6>
<ul>
  <li>Check your blood sugar regularly and track results.</li>
  <li>Monitor blood pressure and cholesterol levels.</li>
  <li>Keep an eye on your feet for cuts, blisters, or infections.</li>
  <li>Get regular eye exams and kidney function tests.</li>
</ul>

<h6 style="color: #c0392b; margin-top: 20px;"><i class="bi bi-exclamation-triangle me-2"></i>Seek Medical Help If</h6>
<ul>
  <li>You experience frequent urination, extreme thirst, or fatigue.</li>
  <li>You notice blurred vision or slow-healing wounds.</li>
  <li>You feel tingling, numbness, or pain in hands and feet.</li>
  <li>You have sudden changes in blood sugar readings.</li>
</ul>

<p style="margin-top: 15px;"><strong>Note:</strong> Diabetes is manageable with the right care plan. Stay in regular contact with your healthcare team and attend all follow-up appointments.</p>
        """

            else:
                decission = "🟢 No Diabetes Detected (Negative)";        
                advice = """
<p>Great news! Your test results do not show signs of diabetes. However, maintaining healthy habits is essential to prevent the onset of diabetes in the future.</p>

<h5 class="mt-4 fw-bold text-primary"><i class="bi bi-shield-check fs-3 me-2 text-success"></i>Continue with These Practices to Manage and Prevent Diabetes ----</h5>

<h6 style="color: #2c3e50; margin-top: 20px;"><i class="bi bi-nutrition me-2"></i>Diet & Nutrition</h6>
<ul>
  <li>Eat a balanced diet rich in whole grains, vegetables, fruits, and lean proteins.</li>
  <li>Limit consumption of sugary foods, sweetened beverages, and processed snacks.</li>
  <li>Control portion sizes to maintain a healthy weight and prevent blood sugar spikes.</li>
  <li>Choose fiber-rich foods like oats, legumes, and brown rice to improve insulin sensitivity.</li>
</ul>

<h6 style="color: #27ae60; margin-top: 20px;"><i class="bi bi-bicycle me-2"></i>Lifestyle</h6>
<ul>
  <li>Engage in regular physical activity — at least 150 minutes per week (e.g., walking, cycling, swimming).</li>
  <li>Avoid tobacco use — it increases the risk of type 2 diabetes and other health issues.</li>
  <li>Limit alcohol intake to moderate levels (if consumed at all).</li>
  <li>Maintain a healthy body weight and body mass index (BMI).</li>
  <li>Get adequate sleep and manage stress through mindfulness or relaxation techniques.</li>
</ul>

<h6 style="color: #8e44ad; margin-top: 20px;"><i class="bi bi-activity me-2"></i>Monitor Your Health</h6>
<ul>
  <li>Get blood sugar levels tested annually, especially if you have a family history of diabetes.</li>
  <li>Check blood pressure and cholesterol regularly as part of routine health checks.</li>
  <li>Watch for early signs of insulin resistance like fatigue, weight gain, or increased thirst.</li>
</ul>

<p style="margin-top: 15px;"><strong>Keep up the good work!</strong> A healthy lifestyle helps you stay diabetes-free and supports your overall well-being.</p>
                """

            return jsonify({"success": True,
                            "prediction": result_text,
                            "advice": advice,
                            "decission": decission})

        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    return render_template('diabetes.html')


# @app.route('/parkinson', methods=['POST','GET'])
# def predict():
#     if request.method == 'POST':
#         try:
#             # Get form values
#             features = [
#                 float(request.form['fo']),
#                 float(request.form['fhi']),
#                 float(request.form['flo']),
#                 float(request.form['Jitter_percent']),
#                 float(request.form['Jitter_Abs']),
#                 float(request.form['RAP']),
#                 float(request.form['PPQ']),
#                 float(request.form['DFA']),
#                 float(request.form['Shimmer']),
#                 float(request.form['Shimmer_dB']),
#                 float(request.form['APQ3']),
#                 float(request.form['APQ5']),
#                 float(request.form['APQ']),
#                 float(request.form['DDA']),
#                 float(request.form['NHR']),
#                 float(request.form['HNR']),
#                 float(request.form['RPDE']),
#                 float(request.form['D2']),
#                 float(request.form['spread1']),
#                 float(request.form['spread2']),
#                 float(request.form['PPE'])
#             ]

#             input_data = np.array([features])
#             prediction = parkinson.predict(input_data)

#             result = "Parkinson's Detected" if prediction[0] == 1 else "Healthy - No Parkinson's Detected"
#             return jsonify({"success": True, "prediction": result})
        
#         except Exception as e:
#             return jsonify({"success": False, "error": str(e)})
#     return render_template('parkinson.html')
@app.route('/parkinson', methods=['GET', 'POST'])
def predict_parkinson():
    if request.method == 'POST':
        try:
            # Extract float values from form for selected features
            input_data = [float(request.form.get(feat, 0)) for feat in selected_features]

            # Prepare DataFrame
            input_df = pd.DataFrame([input_data], columns=selected_features)

            # Scale and predict
            input_scaled = scaler.transform(input_df)
            prediction = model.predict(input_scaled)[0]

            if prediction == 1:
                result = "Parkinson's Detected"
            else:
                result = "Healthy"

            return jsonify({
                "prediction": result,
                "result": int(prediction)
            })

        except Exception as e:
            return jsonify({
                "prediction": f"Error: {str(e)}",
                "result": -1
            })
    return render_template('parkinson.html', features=selected_features)


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

            return jsonify({"success": True, "prediction": result_text, "result": int(prediction)})

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

             # return jsonify({"success": True, "prediction": result_text})
            return jsonify({"success": True, "prediction": result_text, "result": int(prediction)})

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
    gender = request.form['gender']

    profile_pic = None
    if 'profile_pic' in request.files:
        file = request.files['profile_pic']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            profile_pic = f"/static/profile_pics/{filename}"

    cur = mysql.connection.cursor()

    if profile_pic:
        cur.execute("UPDATE users SET username=%s,phone=%s, gender=%s, profile_pic=%s WHERE email=%s",
                    (username, phone, gender, profile_pic, session['email']))
    else:
        cur.execute("UPDATE users SET username=%s, phone=%s, gender=%s WHERE email=%s",
                    (username, phone, gender, session['email']))

    mysql.connection.commit()
    cur.close()

    return jsonify({"success": True, "message": "Profile updated successfully!"})



if __name__ == '__main__':
    app.secret_key = "group10"
    app.run(debug=True)