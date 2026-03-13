from flask import Flask, render_template, request
import mysql.connector
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
load_dotenv()
app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_USE_TLS'] = True
mail = Mail(app)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="portfolio_db"
)
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/resume")
def resume():
    return render_template("resume.html")

@app.route("/project")
def project():
    return render_template("projects.html")

@app.route("/service")
def service():
    return render_template("service.html")

@app.route("/certificates")
def certificates():
    return render_template("certificates.html")

@app.route("/skills")
def skills():
    return render_template("skills.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():

    cursor = db.cursor()

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        subject = request.form["subject"]
        message = request.form["message"]
        query = "INSERT INTO portfolio (name,email,subject,message) VALUES (%s,%s,%s,%s)"
        values = (name,email,subject,message)

        cursor.execute(query, values)
        db.commit()
        msg = Message(
            subject=f"Portfolio Contact: {subject}",
            sender=app.config['MAIL_USERNAME'],
            recipients=[app.config['MAIL_USERNAME']]
        )

        msg.body = f"""
Name: {name}
Email: {email}

Message:
{message}
"""

        mail.send(msg)

    cursor.execute("SELECT * FROM portfolio")
    data = cursor.fetchall()

    return render_template("contact.html", data=data)


if __name__ == "__main__":
    app.run(debug=True)