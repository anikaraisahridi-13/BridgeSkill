import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, session, send_from_directory

from database import Database
from models import User, Student, Mentor

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- CONFIG ----------------
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "ppt", "pptx"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------- HELPER ----------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------- HOME ----------------
@app.route("/")
def index():
    return render_template("index.html")


# ---------------- AUTH ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":

        user = User(
            name=request.form["name"],
            email=request.form["email"],
            password=request.form["password"],
            role=request.form["role"]
        )

        db = Database()
        user.signup(db)
        db.close()

        return redirect("/login")

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        user = User(
            email=request.form["email"],
            password=request.form["password"]
        )

        db = Database()
        data = user.login(db)
        db.close()

        if data:
            session["user"] = data["email"]
            session["role"] = data["role"]

            return redirect("/student" if data["role"] == "student" else "/mentor")

        return "Invalid Email or Password ❌"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------------- STUDENT ----------------
@app.route("/student")
def student():

    if "user" not in session or session.get("role") != "student":
        return redirect("/login")

    db = Database()
    student = Student(email=session["user"])
    mentors = student.get_mentors(db)
    db.close()

    return render_template("student_dashboard.html", mentors=mentors)


@app.route("/request/<int:mentor_id>")
def request_mentor(mentor_id):

    if "user" not in session or session.get("role") != "student":
        return redirect("/login")

    db = Database()
    student = Student(email=session["user"])
    student.request_mentor(db, mentor_id)
    db.close()

    return redirect("/request_success")


@app.route("/request_success")
def success():
    return render_template("request_success.html")


# ---------------- MENTOR ----------------
@app.route("/mentor")
def mentor():

    if "user" not in session or session.get("role") != "mentor":
        return redirect("/login")

    db = Database()
    mentor = Mentor(email=session["user"])
    requests = mentor.get_requests(db)
    db.close()

    return render_template("mentor_dashboard.html", requests=requests)


@app.route("/accept/<int:id>")
def accept(id):

    if session.get("role") != "mentor":
        return redirect("/login")

    db = Database()
    db.execute("UPDATE requests SET status='accepted' WHERE id=%s", (id,))
    db.close()

    return redirect("/mentor")


@app.route("/reject/<int:id>")
def reject(id):

    if session.get("role") != "mentor":
        return redirect("/login")

    db = Database()
    db.execute("UPDATE requests SET status='rejected' WHERE id=%s", (id,))
    db.close()

    return redirect("/mentor")


# ---------------- MENTOR PROFILE ----------------
@app.route("/mentor_profile")
def mentor_profile():

    if "user" not in session or session.get("role") != "mentor":
        return redirect("/login")

    db = Database()
    db.execute("SELECT * FROM users WHERE email=%s", (session["user"],))
    mentor = db.fetchone()
    db.close()

    return render_template("mentor_profile.html", mentor=mentor)


# ---------------- SLIDES ----------------
@app.route("/upload_slide", methods=["GET", "POST"])
def upload_slide():

    if "user" not in session or session.get("role") != "mentor":
        return redirect("/login")

    if request.method == "POST":

        file = request.files.get("file")
        title = request.form.get("title")

        if not file or file.filename == "":
            return "No file selected ❌"

        if allowed_file(file.filename):

            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

            # avoid overwrite
            if os.path.exists(filepath):
                filename = str(os.urandom(6).hex()) + "_" + filename
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

            file.save(filepath)

            db = Database()
            db.execute(
                "INSERT INTO slides(mentor_email,title,filename) VALUES(%s,%s,%s)",
                (session["user"], title, filename)
            )
            db.close()

            return redirect("/mentor")

        return "Invalid file type ❌"

    return render_template("upload_slide.html")


# ---------------- VIEW SLIDES ----------------
@app.route("/slides")
def slides():

    if "user" not in session:
        return redirect("/login")

    db = Database()
    db.execute("SELECT * FROM slides")
    slides = db.fetchall()
    db.close()

    return render_template("slides.html", slides=slides)


# ---------------- FILE SERVING ----------------
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)