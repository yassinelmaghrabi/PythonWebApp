import logging
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class DBManager:
    def __init__(self, database='example', host="db", user="root", password_file=None):
        self.connection = None
        self.cursor = None
        try:
            pf = open(password_file, 'r')
            password = pf.read().strip()
            pf.close()
            self.connection = mysql.connector.connect(
                user=user,
                password=password,
                host=host,
                database=database,
                auth_plugin='mysql_native_password'
            )
            self.cursor = self.connection.cursor()
        except Exception as e:
            logging.error(f"Error connecting to database: {str(e)}")

    def __del__(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
        except Exception as e:
            logging.error(f"Error closing database connection: {str(e)}")

    def populate_db(self):
        try:

            with open('schema.sql', 'r') as file:
                sql_query = file.read()

            self.cursor.execute(sql_query)
            self.connection.commit()
        except Exception as e:
            logging.error(f"Error creating table: {str(e)}")

    def query_titles(self):
        try:
            self.cursor.execute('SELECT * FROM students')
            records = self.cursor.fetchall()
            logging.info(f"Fetched records: {records}")
            return records
        except Exception as e:
            logging.error(f"Error querying titles: {str(e)}")

    def add(self, name, student_id, gpa, age):
        try:
            query = "INSERT INTO students (name, student_id, gpa, age) VALUES (%s, %s, %s, %s)"
            values = (name, student_id, float(gpa), int(age))
            self.cursor.execute(query, values)
            self.connection.commit()
            return 1
        except Exception as e:
            logging.error(f"Error inserting into table: {str(e)}")
            return 0

    def delete(self, stdid):
        try:
            self.cursor.execute("DELETE FROM students WHERE id=%s", (stdid,))
            self.connection.commit()
        except Exception as e:
            logging.error(f"Error deleting student: {str(e)}")


app = Flask(__name__)
app.secret_key = 'secretkey'
conn = None


@app.route("/")
def home():
    global conn
    conn = DBManager(password_file='/run/secrets/db-password')
    conn.populate_db()
    try:
        return render_template('index.html')
    except Exception as e:
        logging.error(f"Error in home route: {str(e)}")
        return "An error occurred."

@app.route("/students")
def students_list():
    global conn
    try:
        if not conn:
            conn = DBManager(password_file='/run/secrets/db-password')
            conn.populate_db()
        rec = conn.query_titles()
        return render_template('students.html', students=rec)
    except Exception as e:
        logging.error(f"Error in home route: {str(e)}")
        return "An error occurred."

@app.post("/add")
def add():
    global conn
    if not conn:
        conn = DBManager(password_file='/run/secrets/db-password')
    try:
        name = request.form.get("studentName")
        student_id = request.form.get("studentId")
        gpa = request.form.get("studentGpa")
        age = request.form.get("studentAge")
        stat = conn.add(name,student_id,gpa,age)
        if stat == 1:
            flash(f"Student {name} has been added", 'success')
        else: 
            flash(f"Student was not added due to incorrect value format/value", "danger")
        return redirect(url_for("home"))
    except Exception as e:
        logging.error(f"Error adding record: {str(e)}")
        return "An error occurred."


@app.get("/delete/<int:std_id>")
def delete(std_id):
    global conn
    if not conn:
        conn = DBManager(password_file='/run/secrets/db-password')
    try:
        conn.delete(std_id)
        return redirect(url_for("students_list"))
    except Exception as e:
        logging.error(f"Error deleting record: {str(e)}")
        return "An error occurred."
