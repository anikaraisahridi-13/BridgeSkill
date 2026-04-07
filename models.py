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
        result = db.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (self.email, self.password)
        )
        return result.fetchone()


class Student(User):

    def get_mentors(self, db):
        result = db.execute("SELECT * FROM mentors")
        return result.fetchall()

    def request_mentor(self, db, mentor_id):
        db.execute(
            "INSERT INTO requests(student_email,mentor_id,status) VALUES(%s,%s,%s)",
            (self.email, mentor_id, "pending")
        )


class Mentor(User):

    def get_requests(self, db):
        result = db.execute("SELECT * FROM requests")
        return result.fetchall()