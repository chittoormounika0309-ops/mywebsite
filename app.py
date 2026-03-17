from flask import Flask, render_template, request, redirect, session
import mysql.connector
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

# Load env
load_dotenv()

app = Flask(__name__)
app.secret_key = "supersecretkey"  # change this in production

# ------------------ MAIL CONFIG ------------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_USE_TLS'] = True

mail = Mail(app)

# ------------------ DATABASE ------------------
def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# ------------------ ROUTES ------------------

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


# ------------------ CONTACT ------------------

@app.route("/contact", methods=["GET", "POST"])
def contact():
    conn = None
    cursor = None
    data = []

    try:
        conn = get_db()
        cursor = conn.cursor()

        if request.method == "POST":
            name = request.form.get("name")
            email = request.form.get("email")
            subject = request.form.get("subject")
            message = request.form.get("message")

            query = """
            INSERT INTO portfolio (name, email, subject, message)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (name, email, subject, message))
            conn.commit()

            # Send email
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

    except Exception as e:
        print("ERROR:", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template("contact.html", data=data)


# ------------------ ADMIN LOGIN ------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # get from .env
        admin_user = os.getenv("ADMIN_USER")
        admin_pass = os.getenv("ADMIN_PASS")

        if username == admin_user and password == admin_pass:
            session["admin"] = True
            return redirect("/admin")
        else:
            return "Invalid credentials"

    return render_template("login.html", error="Invalid username or password")


# ------------------ ADMIN PANEL ------------------

@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")

    conn = None
    cursor = None
    data = []

    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM portfolio ORDER BY id DESC")
        data = cursor.fetchall()

    except Exception as e:
        print("ERROR:", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template("admin.html", data=data)


# ------------------ DELETE ------------------

@app.route("/delete/<int:id>", methods=["POST"])
def delete_message(id):
    if not session.get("admin"):
        return redirect("/login")

    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM portfolio WHERE id = %s", (id,))
        conn.commit()

    except Exception as e:
        print("DELETE ERROR:", e)

    finally:
        cursor.close()
        conn.close()

    return redirect("/admin")


# ------------------ LOGOUT ------------------

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/login")


# ------------------ RUN ------------------

if __name__ == "__main__":
    app.run(debug=True)