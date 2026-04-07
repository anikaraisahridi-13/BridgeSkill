from flask import Flask, render_template, request, redirect, session
from database import Database
from models import User, Student, Mentor

app = Flask(__name__)
app.secret_key = "secret123"


# Landing Page
@app.route("/")
def index():
    return render_template("index.html")


# Signup
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


# Login
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

            if data["role"] == "student":
                return redirect("/student")
            else:
                return redirect("/mentor")

        return "Invalid Email or Password"

    return render_template("login.html")


# Student Dashboard
@app.route("/student")
def student():

    if "user" not in session or session.get("role") != "student":
        return redirect("/login")

    db = Database()
    student = Student(email=session["user"])
    mentors = student.get_mentors(db)
    db.close()

    return render_template("student_dashboard.html", mentors=mentors)


# Request Mentor
@app.route("/request/<int:mentor_id>")
def request_mentor(mentor_id):

    if "user" not in session or session.get("role") != "student":
        return redirect("/login")

    db = Database()
    student = Student(email=session["user"])
    student.request_mentor(db, mentor_id)
    db.close()

    return redirect("/request_success")


# Request Success Page
@app.route("/request_success")
def success():
    return render_template("request_success.html")


# Mentor Dashboard
@app.route("/mentor")
def mentor():

    if "user" not in session or session.get("role") != "mentor":
        return redirect("/login")

    db = Database()
    mentor = Mentor(email=session["user"])
    requests = mentor.get_requests(db)
    db.close()

    return render_template("mentor_dashboard.html", requests=requests)


#  Accept Request
@app.route("/accept/<int:id>")
def accept(id):

    if session.get("role") != "mentor":
        return redirect("/login")

    db = Database()
    db.execute("UPDATE requests SET status='accepted' WHERE id=%s", (id,))
    db.close()

    return redirect("/mentor")


#  Reject Request
@app.route("/reject/<int:id>")
def reject(id):

    if session.get("role") != "mentor":
        return redirect("/login")

    db = Database()
    db.execute("UPDATE requests SET status='rejected' WHERE id=%s", (id,))
    db.close()

    return redirect("/mentor")


# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# Run Server
if __name__ == "__main__":
    app.run(debug=True)