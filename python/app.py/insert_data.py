from flask import Flask, render_template, request
from flask_mysqldb import MySQL
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'formdata'

mysql = MySQL(app)

# Email configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'carinsurance095@gmail.com'  # Corrected access to environment variable
SMTP_PASSWORD = 'anbvovfdtqpummcu'  # Corrected access to environment variable

def send_email(subject, recipient, body):
    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, recipient, msg.as_string())
    except Exception as e:
        print("An error occurred while sending email:", e)

@app.route('/')
def index():
    return render_template('index.html', submitted=False)

@app.route('/submit_form', methods=['POST'])
def submit_form():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO form (name, email, phone, message) VALUES (%s, %s, %s, %s)",
                        (name, email, phone, message))
            mysql.connection.commit()
            cur.close()

            subject_user = 'Thank you for your submission'
            body_user = f'Dear {name},\n\nThank you for submitting the form. We will get back to you shortly.\n\nBest regards,\nThe Home Service Team'
            send_email(subject_user, email, body_user)

            admin_email = 'chithradevi.bchain@gmail.com'
            subject_admin = 'New form submission'
            body_admin = f'A new form submission has been received.\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}'
            send_email(subject_admin, admin_email, body_admin)

            return render_template('index.html', submitted=True)
        except Exception as e:
            print("An error occurred while inserting data:", e)
            return "An error occurred while processing your request."

if __name__ == '__main__':
    app.run(debug=True)
