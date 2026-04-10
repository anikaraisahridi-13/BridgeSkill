import pymysql

class Database:
    def __init__(self):
        self.conn = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="bridgeskill",
            cursorclass=pymysql.cursors.DictCursor
        )
        self.cur = self.conn.cursor()

    def execute(self, query, values=None):
        self.cur.execute(query, values or ())
        if query.strip().lower().startswith(("insert", "update", "delete")):
            self.conn.commit()

    def fetchall(self):
        return self.cur.fetchall()

    def fetchone(self):
        return self.cur.fetchone()

    def close(self):
        self.cur.close()
        self.conn.close()

