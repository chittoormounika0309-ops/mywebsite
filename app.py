from flask import Flask, render_template, request, redirect, session
import mysql.connector
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret")


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_USE_TLS'] = True

mail = Mail(app)

def get_db():
    try:
        host = os.getenv("MYSQLHOST")
        port = os.getenv("MYSQLPORT")
        user = os.getenv("MYSQLUSER")
        password = os.getenv("MYSQLPASSWORD")
        database = os.getenv("MYSQLDATABASE")
        
        print("---- DB DEBUG ----")
        print("HOST:", host)
        print("PORT:", port)
        print("USER:", user)
        print("DB:", database)
        print("------------------")

        if not all([host, port, user, password, database]):
            raise Exception("Missing environment variables ❌")

        conn = mysql.connector.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=database
        )

        print("✅ DATABASE CONNECTED")
        return conn

    except Exception as e:
        print("❌ DB CONNECTION ERROR:", e)
        return None



@app.route("/")
def home():
    return render_template("index.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    data = []

    conn = get_db()
    if conn is None:
        return "❌ Cannot connect to database!!"

    cursor = conn.cursor()

    try:
        if request.method == "POST":
            name = request.form.get("name")
            email = request.form.get("email")
            subject = request.form.get("subject")
            message = request.form.get("message")

            print("FORM:", name, email, subject, message)

            cursor.execute(
                "INSERT INTO portfolio (name, email, subject, message) VALUES (%s,%s,%s,%s)",
                (name, email, subject, message)
            )
            conn.commit()

            print("✅ DATA INSERTED")

            # Email send
            if app.config['MAIL_USERNAME']:
                msg = Message(
                    subject=f"Portfolio Contact: {subject}",
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[app.config['MAIL_USERNAME']]
                )
                msg.body = f"Name: {name}\nEmail: {email}\n\n{message}"
                mail.send(msg)

        cursor.execute("SELECT * FROM portfolio ORDER BY id DESC")
        data = cursor.fetchall()

        print("DATA:", data)

    except Exception as e:
        print("❌ CONTACT ERROR:", e)

    finally:
        cursor.close()
        conn.close()

    return render_template("contact.html", data=data)



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if (
            username == os.getenv("ADMIN_USERNAME")
            and password == os.getenv("ADMIN_PASSWORD")
        ):
            session["admin"] = True
            return redirect("/admin")
        else:
            return render_template("login.html", error="❌ Invalid credentials")

    return render_template("login.html")



@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")

    conn = get_db()
    if conn is None:
        return "❌ Cannot connect to database."

    cursor = conn.cursor()
    data = []

    try:
        cursor.execute("SELECT * FROM portfolio ORDER BY id DESC")
        data = cursor.fetchall()
        print("ADMIN DATA:", data)

    except Exception as e:
        print("❌ ADMIN ERROR:", e)

    finally:
        cursor.close()
        conn.close()

    return render_template("admin.html", data=data)


@app.route("/delete/<int:id>", methods=["POST"])
def delete_message(id):
    if not session.get("admin"):
        return redirect("/login")

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM portfolio WHERE id = %s", (id,))
        conn.commit()
        print("✅ Deleted:", id)

    except Exception as e:
        print("❌ DELETE ERROR:", e)

    finally:
        cursor.close()
        conn.close()

    return redirect("/admin")


@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)