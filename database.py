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
        self.conn.commit()
        return self.cur

    def fetchone(self):
        return self.cur.fetchone()

    def fetchall(self):
        return self.cur.fetchall()

    def close(self):
        self.cur.close()
        self.conn.close()

