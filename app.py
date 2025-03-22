from flask import Flask, render_template, request, redirect, flash,session,url_for,jsonify
from flask_mysqldb import MySQL
import re
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import pickle
import numpy as np

app = Flask(__name__)
app.secret_key = "group10"

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # Change to your MySQL password
app.config['MYSQL_DB'] = 'healthcheck'

mysql = MySQL(app)



# Load the trained model
model_path = 'heart.pkl'
with open(model_path, 'rb') as file:
    model = pickle.load(file)

# Load the trained model
model_path2 = 'diabetes.pkl'
with open(model_path2, 'rb') as file:
    model2 = pickle.load(file)

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

        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO users (email, phone, gender, password) VALUES (%s, %s, %s, %s)", 
                        (email, phone, gender, hashed_password))
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

        if user and check_password_hash(user[4], password):  # user[4] is the password column
            session['logged_in'] = True
            session['email'] = user[1]

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

# Dashboard (Protected Route)
@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        flash("Please log in first.", "warning")
        return redirect('/login')
        
    return render_template('dashboard.html')

# @app.route('/profile')
# def profile():
#     if 'email' in session:
#         return f"User Profile: {session['email']}"
#     return redirect(url_for('login'))

@app.route('/predict', methods=['POST'])
def predict():
    # Extract data from form
    int_features = [float(x) for x in request.form.values()]
    final_features = [np.array(int_features)]
    
    # Make prediction
    prediction = model.predict(final_features)
    output = 'Heart Disease' if prediction[0] == 1 else 'Healthy Heart'

    return render_template('index.html', prediction_text='Prediction: {}'.format(output))

@app.route('/heart_disease')
def heart_disease():
    if 'email' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

# @app.route('/diabetes')
# def diabetes():
#     if 'email' in session:
#         return render_template('diabetes.html')
#     return redirect(url_for('login'))

# @app.route('/diabetes', methods=['GET', 'POST'])
# def diabetes():
#     if request.method == 'POST':
#         # Fetch form data
#         data = {
#             "pregnancies": request.form['pregnancies'],
#             "glucose": request.form['glucose'],
#             "bloodPressure": request.form['bloodPressure'],
#             "skinThickness": request.form['skinThickness'],
#             "insulin": request.form['insulin'],
#             "bmi": request.form['bmi'],
#             "diabetesPedigree": request.form['diabetesPedigree'],
#             "age": request.form['age']
#         }
        
#         # Simulated prediction logic (Replace with ML model)
#         prediction = "Diabetic" if int(data["glucose"]) > 140 else "Not Diabetic"

#         return jsonify({"prediction": prediction})

#     return render_template("diabetes.html") 

@app.route('/heart_prediction', methods=['GET', 'POST'])
def heart_prediction():
    if request.method == 'POST':
        # Fetch form data
        data = {key: request.form[key] for key in request.form}

        # Simulated heart disease prediction logic
        prediction = "Heart Disease Detected" if int(data["chol"]) > 200 else "No Heart Disease"

        return jsonify({"prediction": prediction})

    return render_template("heart_prediction.html")

@app.route('/diabetes', methods=['GET', 'POST'])
def diabetes():
    if request.method == 'POST':
        # Fetch form data
        data = {key: request.form[key] for key in request.form}

        # Simulated diabetes prediction logic (Modify this based on real logic)
        prediction = "Diabetes Detected" if int(data["Glucose"]) > 120 else "No Diabetes"

        return jsonify({"prediction": prediction})

    return render_template("diabetes.html")

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
    #cur.execute("SELECT name, email, phone, gender FROM users WHERE id = %s", (session['user_id'],))
    cur.execute("SELECT email, phone, gender FROM users WHERE email = %s", (session['email'],))
    user = cur.fetchone()
    cur.close()

    if user:
       # return jsonify({"name": user[0], "email": user[1], "phone": user[2], "gender": user[3]})
        return jsonify({"email": user[0], "phone": user[1], "gender": user[2]})
    else:
        return jsonify({"error": "User not found"}), 404


if __name__ == '__main__':
    app.secret_key = "group10"
    app.run(debug=True)
