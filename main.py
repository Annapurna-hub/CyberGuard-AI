from flask import Flask, render_template, request
import pandas as pd
import pickle
import sqlite3

app = Flask(__name__)

# Load model
model = pickle.load(open("model.pkl", "rb"))

@app.route('/', methods=['GET', 'POST'])
def login():

    error = None

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:
            return render_template('assessment.html')
            

        else:
            error = "Invalid Email or Password"

    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users(fullname,email,password) VALUES(?,?,?)",
                (fullname, email, password)
            )

            conn.commit()

        except:
            conn.close()
            return "User already exists!"

        conn.close()

        return render_template('login.html')

    return render_template('register.html')
@app.route('/dashboard', methods=['GET', 'POST'])
def index():
    prediction = None
    suggestions = []
    threats = []
    


    if request.method == 'POST':
        try:
            data = pd.read_csv("data.csv")

            # Keep original row BEFORE encoding
            original_data = data.copy()

            # Drop unnecessary columns
            data = data.drop(['timestamp', 'src_ip', 'dst_ip'], axis=1)

            # Encode
            data = pd.get_dummies(data)

            # Sample for ML prediction
            sample = data.drop('label', axis=1).iloc[0].values.reshape(1, -1)

            result = model.predict(sample)

            # 🔥 SMART FEATURE-BASED ANALYSIS
            row = original_data.iloc[0]

            # Rule 1: High traffic
            if row['bytes_sent'] > 1000 or row['bytes_received'] > 1000:
                threats.append("Possible DDoS attack (high traffic detected)")
                suggestions.append("Monitor network traffic and apply rate limiting")

            # Rule 2: External access
            if row['is_internal'] == 0:
                threats.append("External network access detected")
                suggestions.append("Use firewall and restrict external access")

            # Rule 3: Suspicious protocol
            if row['protocol'] == "ICMP":
                threats.append("Suspicious protocol usage (ICMP)")
                suggestions.append("Monitor unusual protocol activity")

            # 🔹 Prediction
            if result[0] == 1:
                prediction = "Safe"
                if not suggestions:
                    suggestions.append("System is secure. Maintain regular updates.")
            else:
                prediction = "Not Safe"
                if not suggestions:
                    suggestions = [
                        "Enable Multi-Factor Authentication",
                        "Use strong and unique passwords",
                        "Keep system updated",
                        "Install firewall protection"
                    ]

        except Exception as e:
            prediction = str(e)

    return render_template('index.html', prediction=prediction, suggestions=suggestions, threats=threats)
@app.route('/results', methods=['POST'])
def results():


    risk_score = 0
    recommendations = []

    security_level = int(request.form['security_level'])
    mfa = request.form['mfa']
    encryption = request.form['encryption']
    exposure = request.form['exposure']
    firmware = request.form['firmware']
    platform = request.form['platform']
    email = "Current User"

    if security_level < 50:
        risk_score += 20
        recommendations.append("Increase overall security level")

    if mfa == "Disabled":
        risk_score += 20
        recommendations.append("Enable Multi-Factor Authentication")

    if encryption == "Disabled":
        risk_score += 20
        recommendations.append("Enable Encryption")

    if exposure == "Medium":
        risk_score += 15
        recommendations.append("Reduce public exposure")

    if exposure == "High":
        risk_score += 30
        recommendations.append("Restrict external access immediately")

    if firmware == "Outdated":
        risk_score += 20
        recommendations.append("Update firmware regularly")
    # Platform-specific recommendations

    if platform == "AWS":
        recommendations.append("Enable AWS IAM Policies")
        recommendations.append("Enable AWS CloudTrail")
        recommendations.append("Use AWS Security Hub")

    elif platform == "Azure":
        recommendations.append("Enable Azure Defender")
        recommendations.append("Configure Network Security Groups")
        recommendations.append("Enable Azure Monitor")

    elif platform == "IoT Device":
        recommendations.append("Disable Unused Ports")
        recommendations.append("Enable Device Authentication")
        recommendations.append("Perform Regular Firmware Audits")

    if risk_score <= 30:
        risk_level = "LOW"
    elif risk_score <= 60:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    risk_score = min(risk_score, 100)
    reduced_risk = max(0, risk_score - 40)

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO assessments(email, platform, risk_score, risk_level)
        VALUES (?, ?, ?, ?)
        """,
        (email, platform, risk_score, risk_level)
    )

    conn.commit()
    conn.close()

    phishing = 20
    ddos = 20
    data_leak = 20

    threat1 = "Phishing"
    threat2 = "DDoS"
    threat3 = "Data Leakage"

    if platform == "AWS":
        threat1 = "IAM Misconfiguration"
        threat2 = "S3 Bucket Exposure"
        threat3 = "API Abuse"

    elif platform == "Azure":
        threat1 = "Identity Attack"
        threat2 = "NSG Misconfiguration"
        threat3 = "Resource Exposure"

    elif platform == "IoT Device":
        threat1 = "Device Hijacking"
        threat2 = "Firmware Tampering"
        threat3 = "Botnet Infection"

    if mfa == "Disabled":
        phishing += 60

    if encryption == "Disabled":
        data_leak += 60

    if exposure == "High":
        ddos += 60

    elif exposure == "Medium":
        ddos += 30

    def get_color(value):

        if value < 40:
            return "#28a745"

        elif value < 70:
            return "#ffc107"

        else:
            return "#dc3545"

    phishing_color = get_color(phishing)
    ddos_color = get_color(ddos)
    data_leak_color = get_color(data_leak)

    return render_template(
    'results.html',
    risk_score=risk_score,
    risk_level=risk_level,
    recommendations=recommendations,
    reduced_risk=reduced_risk,
    phishing=phishing,
    ddos=ddos,
    data_leak=data_leak,
    threat1=threat1,
    threat2=threat2,
    threat3=threat3,
    phishing_color=phishing_color,
    ddos_color=ddos_color,
    data_leak_color=data_leak_color
)



@app.route('/history')
def history():

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM assessments ORDER BY id DESC"
    )

    assessments = cursor.fetchall()

    conn.close()

    return render_template(
        'history.html',
        assessments=assessments
    )
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM assessments WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return history()
@app.route('/assessment')
def assessment():
    return render_template('assessment.html')
    
if __name__ == '__main__':
    app.run(debug=True)