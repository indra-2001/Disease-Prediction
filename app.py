from flask import Flask, render_template, request, redirect, flash,session,url_for,jsonify
from flask_mysqldb import MySQL
import re
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import pickle
import numpy as np
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
app.secret_key = "group10"

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
parkinson = pickle.load(open('parkinson.pkl', 'rb'))
kidney_model =  pickle.load(open('kidney_disease.sav', 'rb'))
Breast_Cancer_model = pickle.load(open('Breast_Cancer.sav', 'rb'))
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
            session['profile_pic'] = user[6]
            session['phone'] = user[3]
            session['gender'] = user[4]

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

            return jsonify({"success": True, "prediction": result_text})

        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    return render_template('heart_prediction.html')

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

@app.route('/parkinson', methods=['POST','GET'])
def predict():
    if request.method == 'POST':
        try:
            # Get form values
            features = [
                float(request.form['fo']),
                float(request.form['fhi']),
                float(request.form['flo']),
                float(request.form['Jitter_percent']),
                float(request.form['Jitter_Abs']),
                float(request.form['RAP']),
                float(request.form['PPQ']),
                float(request.form['DFA']),
                float(request.form['Shimmer']),
                float(request.form['Shimmer_dB']),
                float(request.form['APQ3']),
                float(request.form['APQ5']),
                float(request.form['APQ']),
                float(request.form['DDA']),
                float(request.form['NHR']),
                float(request.form['HNR']),
                float(request.form['RPDE']),
                float(request.form['D2']),
                float(request.form['spread1']),
                float(request.form['spread2']),
                float(request.form['PPE'])
            ]

            input_data = np.array([features])
            prediction = parkinson.predict(input_data)

            result = "Parkinson's Detected" if prediction[0] == 1 else "Healthy - No Parkinson's Detected"
            return render_template('parkinson.html', prediction_text=result)

        except Exception as e:
            return render_template('parkinson.html', prediction_text=f"Error: {str(e)}")

@app.route('/Breast_cancer', methods=['GET', 'POST'])
def Breast_cancer():
    if request.method == 'POST':
        try:
            # Extract form values and convert them into float
            input_data = [float(request.form[key]) for key in [
                                                            'radius_mean', 'texture_mean', 'perimeter_mean', 'area_mean', 'smoothness_mean',
                                                            'compactness_mean', 'concavity_mean', 'concave points_mean', 'symmetry_mean', 'fractal_dimension_mean',
                                                            'radius_se ', 'texture_se', 'perimeter_se', 'area_se', 'smoothness_se',
                                                            'compactness_se', 'concavity_se', 'concave points_se', 'symmetry_se', 'fractal_dimension_se',
                                                            'radius_worst', 'texture_worst', 'perimeter_worst', 'area_worst', 'smoothness_worst',
                                                            'compactness_worst', 'concavity_worst', 'concave points_worst', 'symmetry_worst', 'fractal_dimension_worst'
                                                            ]]
            # Convert into numpy array for model prediction
            input_array = np.array(input_data).reshape(1, -1)

            # Predict using model
            prediction = Breast_Cancer_model.predict(input_array)[0]

            # Determine result
            result_text = "The Breast Cancer is Benign" if prediction == 1 else "The Breast cancer is Malignant"

            return jsonify({"success": True, "prediction": result_text})

        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    return render_template('Breast_cancer.html')



@app.route('/kidney', methods=['GET', 'POST'])
def kidney():
    if request.method == 'POST':
        try:
            # Extract form values and convert them into float

            
            input_data = [request.form[key] for key in [ 'Age', 'Blood Pressure', 'Specific gravity(Urine cocentration)', 'Albumin',
                                                        'Blood Sugar', 'Red Blood cells in Urine', 'Pus Cells in urine',
                                                        'Pus Cell Clumps in Urine', 'Bacteria in Urine', 'Blood Glucose',
                                                        'Blood Urea ', 'Serum Creatinine', 'Sodium', 'Potassium', 'Hemoglobin',
                                                        'Packed Cell Volume', 'White Blood Cell Count (/cubic mm)',
                                                        'Red Blood Cell Count (million/cumm)', 'Hypertension', 'Diabetes',
                                                        'Coronary Artery Disease', 'Appetite', 'Pedal Edema (swelling in leg/feet)',
                                                        'Anemia']]

            # input_data = [request.form[key] for key in [ 'age', 'bp', 'sg', 'al', 'su', 'rbc', 'pc', 'pcc', 'ba',
            #                                             'bgr', 'bu', 'sc', 'sod', 'pot', 'hemo', 'pcv',
            #                                             'wc', 'rc', 'htn', 'dm', 'cad', 'appet', 'pe', 'ane']]
            
            # Convert into numpy array for model prediction
            input_array = np.array(input_data).reshape(1, -1)

            # Predict using model
            prediction = kidney_model.predict(input_array)[0]

            # Determine result
            result_text = "The prediction indicates a positive case of chronic kidney disease." if prediction == 0 else "You are predicted safe from Chronic Kidney disease (Negative)"

            return jsonify({"success": True, "prediction": result_text})

        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    return render_template('kidney.html')




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


