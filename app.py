from flask import Flask, render_template, request, redirect, flash,session,url_for,jsonify,send_from_directory
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os
import joblib
import io
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import pickle
import numpy as np
import pandas as pd
from datetime import timedelta
from flask_mail import Mail, Message # type: ignore
from itsdangerous import URLSafeTimedSerializer
import dotenv # type: ignore
from datetime import datetime
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from tensorflow.keras.models import load_model # type: ignore
from tensorflow.keras.preprocessing.image import load_img, img_to_array # type: ignore
import warnings
warnings.filterwarnings('ignore')


dotenv.load_dotenv()
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

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
app.config['MYSQL_PASSWORD'] = 'pwd1234'  # Change to your MySQL password
app.config['MYSQL_DB'] = 'healthcheck'

mysql = MySQL(app)

# File Upload Configuration
UPLOAD_FOLDER = "static/profile_pics"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Load the trained model
#heart_model = pickle.load(open('heart_disease_model.sav', 'rb'))
# with open("heart_disease_model.pkl", "rb") as f:
#     heart_model = pickle.load(f)

# Load model
with open("heart_model.pkl", "rb") as f:
    heart_model = pickle.load(f)

# Load scaler
with open("scaler.pkl", "rb") as f:
    scalerH = pickle.load(f)

diabetes_model = pickle.load(open('diabetes_model.sav', 'rb')) 
kidney_model =  pickle.load(open('kidney_disease(short).sav', 'rb'))
Breast_Cancer_model = pickle.load(open('Breast_Cancer.sav', 'rb'))
Liver_model = pickle.load(open('liver_model.sav', 'rb'))
Liver_scaler_model = pickle.load(open('liver_scaler.sav', 'rb'))
Fatty_Liver_model = pickle.load(open('fatty_liver_model.sav', 'rb'))
Fatty_Liver_scaler_model = pickle.load(open('fatty_liver_scaler.sav', 'rb'))

# Load brain tumor classification model
tumor_model = load_model("model.h5")

# Define class labels in same order as during training
tumor_class_labels = ['glioma', 'meningioma', 'notumor', 'pituitary']

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
         # Check if user is admin
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['admin'] = True
            session['email'] = email
            # session['username'] = "Indra"
            session['username'] = "Group10"
            flash("Admin login successful!", "success")
            return redirect('/admin/dashboard')
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        print(user)
        cur.close()

        if user[8] == 'blocked':  
                flash("Your account is blocked. Please contact admin.", "danger")
                return redirect('/login')
        
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
            #reset_url = url_for('reset_password_token', token=token, _external=True)
            reset_url = request.host_url.rstrip('/') + url_for('reset_password_token', token=token)


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

# About Route
@app.route('/aboutD')
def aboutD():
    return render_template('aboutD.html')

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
                float(request.form.get('Age', 0)),
                float(request.form.get('Sex', 0)),
                float(request.form.get('Chest Pain Type', 0)),
                float(request.form.get('Resting Blood Pressure', 0)),
                float(request.form.get('Cholesterol', 0)),
                float(request.form.get('Fasting Blood Sugar > 120 mg/dl', 0)),
                float(request.form.get('Resting ECG Results', 0)),
                float(request.form.get('Max Heart Rate Achieved', 0)),
                float(request.form.get('Exercise Induced Angina', 0)),
                float(request.form.get('ST Depression Induced by Exercise', 0)),
                float(request.form.get('Slope of Peak Exercise ST Segment', 0)),
                float(request.form.get('Number of Major Vessels Colored by Fluoroscopy', 0)),
                float(request.form.get('Thalassemia', 0))
            ]

            # Convert into numpy array for model prediction
            input_array = np.array(input_data).reshape(1, -1)

            # Scale the input using the loaded scaler
            scaled_input = scalerH.transform(input_array)

            # Predict using the model
            prediction = heart_model.predict(scaled_input)[0]

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

@app.route('/diabetes', methods=['GET', 'POST'])
def diabetes():
    if request.method == 'POST':
        try:
            # Extract form values and convert them into float
            input_data = [float(request.form[key]) for key in ['Pregnancies (times)', 'Glucose Level (mg/dL)', 'Blood Pressure (mm Hg)', 
                                                               'Skin Thickness (mm)', 'Insulin (μU/mL)', 'BMI (kg/m²)', 
                                                               'Diabetes Pedigree Function', 'Age (years)']]
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

model = joblib.load('parkinsons_model.pkl')
scaler = joblib.load('scaler1.pkl')


@app.route('/parkinson', methods=['GET','POST'])
def predict_parkinson():
    if request.method == 'POST':
        try:
            # Get data from form
            input_features = [
                float(request.form['fo']),
                float(request.form['fhi']),
                float(request.form['flo']),
                float(request.form['jitter']),
                float(request.form['shimmer']),
                float(request.form['nhr']),
                float(request.form['hnr']),
                float(request.form['rpde']),
            ]

            # Reshape and scale input
            scaled_input = scaler.transform([input_features])
            prediction = model.predict(scaled_input)[0]

            result = "Parkinson's Detected" if prediction == 1 else "Healthy"
            return jsonify({"success": True, "prediction": result, "result": int(prediction)})
            
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})
    return render_template('parkinson.html')



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


@app.route('/fatty_liver', methods=['GET', 'POST'])
def fatty_liver():
    if request.method == 'POST':
        try:
            # Extract form values and convert them into float
            input_data = [float(request.form[key]) for key in [
                                                                    "Age",
                                                                    "Gender",
                                                                    "Body_Mass_Index",
                                                                    "ALT",
                                                                    "AST",
                                                                    "GGT",
                                                                    "Triglycerides",
                                                                    "Glucose",
                                                                    "Total_Cholesterol",
                                                                    "HDL",
                                                                    "LDL"
                                                                ]]
            #input_array = np.array(input_data).reshape(1, -1)
            input_scaled = Fatty_Liver_scaler_model.transform([input_data])

            # Predict using model
            prediction = Fatty_Liver_model.predict(input_scaled)

            # Determine result
            result_text = "The prediction indicates a Severe illness." if prediction == 0 else "The prediction indicates a mild illness."

             # return jsonify({"success": True, "prediction": result_text})
            return jsonify({"success": True, "prediction": result_text, "result": int(prediction)})

        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    return render_template('fatty_liver.html')




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

# @app.route("/TDEE")
# def tdee():
#     return render_template("TDEE.html")

@app.route("/HydrationCalculator")
def hydration_calculator():
    return render_template("Hydration Calculator.html")

@app.route("/NutrientCalculator")
def nutrient_calculator():
    return render_template("nutrient.html")

@app.route("/body_weight_Calculator")
def body_weight_calculator():
    return render_template("body_weight_calculator.html")



@app.route('/depression', methods=['GET', 'POST'])
def depression():
    if request.method == 'POST':
        try:
            scores = []
            for i in range(1, 10):
                val = request.form.get(f'q{i}')
                scores.append(int(val) if val else 0)

            total_score = sum(scores)

            # Generate message based on PHQ-9 scoring scale
            if total_score <= 4:
                message = "😊 Your depression score is low. You are likely experiencing minimal or no depression symptoms. Keep taking care of your mental health!"
            elif total_score <= 9:
                message = "😐 You are showing some mild depressive symptoms. Consider trying mindfulness, regular activity, or talking to someone you trust."
            elif total_score <= 14:
                message = "⚠️ Your score suggests moderate depression. Speaking to a mental health professional would be beneficial."
            elif total_score <= 19:
                message = "⚠️ You may be experiencing moderately severe depression. Please consult a healthcare provider soon."
            else:
                message = "🚨 Your score indicates severe depression. Immediate professional help is strongly recommended."

            
            return jsonify({"score": total_score, "message": message})
        except Exception as e:
            return jsonify({"error": str(e)})
    
    return render_template("depression.html")


'''@app.route('/stress_screening', methods=['GET', 'POST'])
def stress_screening():
    if request.method == 'POST':
        try:
            answers = {1: 4, 2: 4, 3: 4, 4: 0, 5: 0, 6: 4, 7: 0, 8: 0, 9: 4, 10: 4}
            total_score = 0
            positive_questions = {4, 5, 7, 8}
            for i in range(1, 11):
                score = answers[i]
                if i in positive_questions:
                    score = 4 - score  # Reverse scoring
                    print(f"Q{i}: adjusted score = {score}")
                    total_score += score

            # Interpret PSS-10 score
            if total_score <= 13:
                message = "😊 Low stress. You're managing things well—keep it up!"
            elif total_score <= 26:
                message = "😐 Moderate stress. Consider stress-reducing activities like mindfulness, sleep, or exercise."
            else:
                message = "🚨 High stress. Prioritize self-care and consider speaking to a mental health professional."

            print(f"Total score: {total_score}, Message: {message}")
            return jsonify({"score": total_score, "message": message})

        except Exception as e:
            return jsonify({"error": f"Server error: {str(e)}"}), 500

    return render_template("Stress_question_answer.html")
'''

@app.route('/stress_screening', methods=['GET', 'POST'])
def stress_question_answer():
    if request.method == 'POST':
        try:
            #print("Form data:",request.form)
            scores = []
            #reverse_scored_items = [4, 5, 7, 8]  # PSS-10 reverse scoring (1-indexed)

            for i in range(1, 11):
                val = request.form.get(f'q{i}', None)
                if val is None or not val.isdigit():
                    return jsonify({"error": f"Invalid or missing answer for question {i}"})

                score = int(val)

                # Apply reverse scoring
                #if i in reverse_scored_items:
                    #score = 4 - score  # Reverse the score (assuming scale 0 to 4)

                scores.append(score)

            total_score = sum(scores)

            # Interpret stress levels (based on general PSS-10 interpretation)
            if total_score <= 13:
                message = "😊 Low stress. You seem to be managing things well."
            elif total_score <= 26:
                message = "😐 Moderate stress. Some stress is normal, but try relaxation techniques or mindfulness."
            else:
                message = "⚠️ High stress. Consider speaking with a counselor or therapist to find support strategies."


            return jsonify({"score": total_score, "message": message})

        except Exception as e:
            return jsonify({"error": str(e)})

    return render_template("Stress_question_answer.html")




@app.route('/anxiety', methods=['GET', 'POST'])
def anxiety():
    if request.method == 'POST':
        try:
            scores = [int(request.form.get(f'q{i}', 0)) for i in range(1, 8)]
            total_score = sum(scores)

            if total_score <= 4:
                message = "😊 Minimal anxiety. You're likely doing well, but keep maintaining your mental wellness habits."
            elif total_score <= 9:
                message = "😐 Mild anxiety symptoms. Practicing relaxation techniques may help. Monitor your feelings."
            elif total_score <= 14:
                message = "⚠️ Moderate anxiety. Consider seeking support from a counselor or therapist."
            else:
                message = "🚨 Severe anxiety. Please consult a mental health professional as soon as possible."

            return jsonify({"score": total_score, "message": message})
        except Exception as e:
            return jsonify({"error": str(e)})
    
    return render_template("anxiety.html")



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

def predict_brain_tumor(image_path):
    img_size = 256
    img = load_img(image_path, target_size=(img_size, img_size))
    img_array = img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    predictions = tumor_model.predict(img_array)
    pred_index = np.argmax(predictions)
    confidence = np.max(predictions)

    predicted_label = tumor_class_labels[pred_index]
    if predicted_label == 'notumor':
        return "No Tumor Detected", confidence
    else:
        return f"Tumor Detected: {predicted_label.title()}", confidence


@app.route('/tumor', methods=['GET', 'POST'])
def tumor_detection():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            original_filename = secure_filename(file.filename)

            # Generate a timestamp string (e.g., 20250515_153045)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{original_filename}"

            # TEMP: Save file first to a generic location
            temp_path = os.path.join("static/tumor", filename)
            file.save(temp_path)

            # Predict from saved file
            result_text, confidence = predict_brain_tumor(temp_path)

            # Determine class label folder name
            predicted_label = result_text.split(":")[-1].strip().lower().replace(" ", "") if "Tumor" in result_text else "notumor"

            # Create class-specific subfolder (e.g., static/tumor/glioma)
            save_folder = os.path.join("static/tumor", predicted_label)
            os.makedirs(save_folder, exist_ok=True)

            # Final file path
            final_path = os.path.join(save_folder, filename)

            # Move file to final subfolder
            os.rename(temp_path, final_path)

            return render_template('brain_tumor.html',
                                   result=result_text,
                                   confidence=f"{confidence * 100:.2f}%",
                                   file_path=f"/{final_path.replace(os.sep, '/')}")
    return render_template('brain_tumor.html', result=None)


# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Load the model and features for typhoid
try:
    model_path = os.path.join(os.path.dirname(__file__), 'typhoid_model_best8.sav')
    features_path = os.path.join(os.path.dirname(__file__), 'typhoid_top8_features.sav')

    Typhoid_model = joblib.load(model_path)
    top_features = joblib.load(features_path)

except Exception as e:
    print(f"Error loading model or features: {e}")
    exit(1)

# Ensure top_features is a list of feature names
if not isinstance(top_features, list):
    print("Error: 'top_features' should be a list of feature names.")
    exit(1)

@app.route('/typhoid', methods=['GET', 'POST'])
def typhoid():
    if request.method == 'POST':
        try:
            if not request.form:
                return jsonify({"success": False, "error": "No form data received."}), 400

            input_data = []
            for feature in top_features:
                try:
                    value = request.form.get(feature)
                    if value is None:
                        return jsonify({"success": False, "error": f"Missing data for feature: {feature}"}), 400
                    input_data.append(float(value))
                except ValueError:
                    return jsonify({"success": False, "error": f"Invalid data type for {feature}. Must be a number."}), 400

            input_array = np.array(input_data).reshape(1, -1)

            try:
                prediction = Typhoid_model.predict(input_array)[0]
                probabilities = Typhoid_model.predict_proba(input_array)[0]
            except Exception as model_err:
                return jsonify({"success": False, "error": f"Error during prediction: {model_err}"}), 500

            result_text = "The patient is predicted to NOT have Typhoid." if prediction == 0 else "The patient is predicted to have Typhoid."

            response_data = {
                "success": True,
                "prediction": result_text,
                "result": int(prediction),
                "probability_no_typhoid": probabilities[0],
                "probability_typhoid": probabilities[1]
            }
            return jsonify(response_data)

        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"
            print(error_message)
            return jsonify({"success": False, "error": error_message}), 500

    # This part handles GET requests to /typhoid, if you want it to show the form as well
    # Otherwise, you can remove the `return render_template` line from this block
    return render_template('typhoid.html', features=top_features)

# @app.route("/stress")
# def stress():
#     return render_template("stress.html")

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' in session:
        return render_template('admin_dashboard.html', admin_name=session['username'])
    else:
        flash("Unauthorized access. Please log in as admin.", "danger")
        return redirect('/login')
    

@app.route('/admin/users')
def view_users():
    if 'admin' not in session:
        return redirect('/login')
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, username, email, phone, gender,status FROM users")
    users = cur.fetchall()
    cur.close()
    return render_template('admin_users.html', users=users)

@app.route('/delete_user/<int:id>')
def delete_user(id):
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT username FROM users WHERE id = %s", (id,))
    user = cursor.fetchone()

    if user:
        username = user[0]

        cursor.execute("DELETE FROM health_reports WHERE username = %s", (username,))
        cursor.execute("DELETE FROM user_activity WHERE username = %s", (username,))

        cursor.execute("DELETE FROM users WHERE id = %s", (id,))

        mysql.connection.commit()

    return redirect(url_for('view_users')) 

@app.route('/admin/block_user/<int:id>')
def block_user(id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE users SET status = 'blocked' WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash("User blocked successfully!", "warning")
    return redirect(url_for('view_users'))


@app.route('/admin/unblock_user/<int:id>')
def unblock_user(id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE users SET status = 'active' WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash("User unblocked successfully!", "success")
    return redirect(url_for('view_users'))

@app.route('/admin/view_user/<int:id>')
def view_user_details(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, username, email, phone, gender, profile_pic, created_at, status FROM users WHERE id = %s", (id,))
    row = cur.fetchone()
    if row:
        user = {
            'id': row[0],
            'username': row[1],
            'email': row[2],
            'phone': row[3],
            'gender': row[4],
            'profile_pic': row[5],
            'created_at': row[6],
            'status': row[7]
        }
        return render_template('view_user_details.html', user=user)
    else:
        flash("User not found", "danger")
        return redirect(url_for('view_users'))


@app.route('/admin/view_bmi_bmr')
def view_bmi_bmr_history():
    if 'admin' not in session:
        return redirect('/login')

    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    filter_username = request.args.get('filter_username', '')
    filter_category = request.args.get('filter_category', '')

    cur = mysql.connection.cursor()

    cur.execute("SELECT DISTINCT username FROM health_reports")
    usernames = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT DISTINCT category FROM health_reports")
    categories = [row[0] for row in cur.fetchall()]

    query = "SELECT id, username, height, weight, category, result_value FROM health_reports WHERE 1"
    filters = []
    params = []

    if filter_username:
        filters.append("username = %s")
        params.append(filter_username)
    if filter_category:
        filters.append("category = %s")
        params.append(filter_category)

    if filters:
        query += " AND " + " AND ".join(filters)

    count_query = f"SELECT COUNT(*) FROM ({query}) AS sub"
    cur.execute(count_query, params)
    total = cur.fetchone()[0]
    total_pages = (total + per_page - 1) // per_page

    offset = (page - 1) * per_page
    query += " ORDER BY id DESC LIMIT %s OFFSET %s"
    cur.execute(query, (*params, per_page, offset))
    users = cur.fetchall()
    cur.close()

    return render_template("admin_bmi_bmr_activity.html",
                           users=users,
                           page=page,
                           per_page=per_page,
                           total_pages=total_pages,
                           filter_username=filter_username,
                           filter_category=filter_category,
                           usernames=usernames,
                           categories=categories)


@app.route('/admin/view_predictions')
def view_prediction_history():
    if 'admin' not in session:
        return redirect('/login')

    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    filter_username = request.args.get('filter_username', '').strip()
    filter_disease = request.args.get('filter_disease', '').strip()

    cur = mysql.connection.cursor()

    # Unique dropdown data
    cur.execute("SELECT DISTINCT username FROM user_activity")
    usernames = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT DISTINCT disease_name FROM user_activity")
    diseases = [row[0] for row in cur.fetchall()]

    # Filtering
    base_query = "SELECT id, username, disease_name, prediction_result, pdf_report, created_at FROM user_activity WHERE 1"
    filters = []
    params = []

    if filter_username:
        filters.append("username = %s")
        params.append(filter_username)
    if filter_disease:
        filters.append("disease_name = %s")
        params.append(filter_disease)

    if filters:
        base_query += " AND " + " AND ".join(filters)

    count_query = f"SELECT COUNT(*) FROM ({base_query}) AS sub"
    cur.execute(count_query, params)
    total = cur.fetchone()[0]
    total_pages = (total + per_page - 1) // per_page

    offset = (page - 1) * per_page
    base_query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
    cur.execute(base_query, (*params, per_page, offset))
    users = cur.fetchall()
    cur.close()

    return render_template("admin_prediction_history.html",
                           users=users,
                           page=page,
                           per_page=per_page,
                           total_pages=total_pages,
                           filter_username=filter_username,
                           filter_disease=filter_disease,
                           usernames=usernames,
                           diseases=diseases)



@app.route('/admin/view-doctors')
def view_doctors():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM doctors ORDER BY specialization, name")
    doctors = cur.fetchall()
    cur.close()

    # Group by specialization
    grouped = {}
    for doc in doctors:
        grouped.setdefault(doc['specialization'], []).append(doc)

    return render_template('view_doctors.html', grouped=grouped)


@app.route('/admin/add-doctor', methods=['GET', 'POST'])
def add_doctor():
    if request.method == 'POST':
        name = request.form['name']
        specialization = request.form['specialization']
        experience = request.form['experience']
        contact = request.form['contact']  # <-- New field
        photo = request.files['photo']

        photo_path = os.path.join('static/Doctors_Photo', secure_filename(photo.filename))
        photo.save(photo_path)

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO doctors (name, specialization, experience, contact, photo_path) 
            VALUES (%s, %s, %s, %s, %s)
        """, (name, specialization, experience, contact, photo_path))
        mysql.connection.commit()
        cur.close()

        flash("Doctor added successfully!", "success")
        return redirect(url_for('view_doctors'))

    specializations = ['Cardiologist', 'Hepatologist', 'Diabetologist', 'Nephrologist', 'Oncologist',
                       'Neurologist', 'Pulmonologist', 'Infectious Disease Specialist', 'Gastroenterologist']
    return render_template('add_doctor.html', specializations=specializations)

@app.route("/get_doctors")
def get_doctors():
    specialization = request.args.get("specialization")
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT name, specialization, experience, contact, photo_path FROM doctors WHERE specialization = %s", [specialization])
    rows = cursor.fetchall()

    doctors = []
    for row in rows:
        doctors.append({
            "name": row[0],
            "specialization": row[1],
            "experience": row[2],
            "contact": row[3],
            "photo_path": row[4]
        })
    return jsonify(doctors)

@app.route('/edit_doctor/<int:doctor_id>', methods=['GET', 'POST'])
def edit_doctor(doctor_id):
    doctor = get_doctor_by_id(doctor_id)  # Fetch current data

    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        experience = request.form['experience']
        specialization = request.form['specialization']

        photo = request.files.get('photo')
        photo_path = doctor['photo_path']  # Default to existing path

        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(photo_path)
            photo_path = photo_path.replace("\\", "/")  # Normalize path for HTML

        update_doctor(doctor_id, name, contact, experience, specialization, photo_path)
        return redirect(url_for('view_doctors'))

    return render_template('edit_doctor.html', doctor=doctor)

@app.route('/delete_doctor/<int:doctor_id>')
def delete_doctor(doctor_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM doctors WHERE id = %s", (doctor_id,))
    mysql.connection.commit()
    return redirect(url_for('view_doctors'))

def update_doctor(doctor_id, name, contact, experience, specialization, photo_path):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        UPDATE doctors SET name=%s, contact=%s, experience=%s, specialization=%s, photo_path=%s
        WHERE id=%s
    """, (name, contact, experience, specialization, photo_path, doctor_id))
    mysql.connection.commit()
    cursor.close()

def get_doctor_by_id(doctor_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM doctors WHERE id = %s", (doctor_id,))
    doctor = cursor.fetchone()
    cursor.close()
    return doctor


    
if __name__ == '__main__':
    app.secret_key = "group10"
    app.run(debug=True)