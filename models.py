class User:
    def __init__(self, name=None, email=None, password=None, role=None):
        self.name = name
        self.email = email
        self.password = password
        self.role = role

    def signup(self, db):
        db.execute(
            "INSERT INTO users(name,email,password,role) VALUES(%s,%s,%s,%s)",
            (self.name, self.email, self.password, self.role)
        )

    def login(self, db):
        db.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (self.email, self.password)
        )
        return db.fetchone()   # ✅ FIXED


class Student(User):

    def get_mentors(self, db):
        db.execute("SELECT * FROM mentors")
        return db.fetchall()   # ✅ FIXED

    def request_mentor(self, db, mentor_id):
        db.execute(
            "INSERT INTO requests(student_email,mentor_id,status) VALUES(%s,%s,%s)",
            (self.email, mentor_id, "pending")
        )


class Mentor(User):

    def get_requests(self, db):
        db.execute("SELECT * FROM requests")
        return db.fetchall()   # ✅ FIXED