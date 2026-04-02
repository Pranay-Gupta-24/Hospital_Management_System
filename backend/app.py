from flask import Flask, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "Hospital Management Backend Running"})



from database import get_db_connection
@app.route('/init-db')
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT NOT NULL,
            fees INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          age INTEGER NOT NULL,
          disease TEXT NOT NULL,
          contact TEXT NOT NULL
         )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS appointments (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          patient_id INTEGER,
          doctor_id INTEGER,
          date TEXT,
          time TEXT
         )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS wards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    capacity INTEGER NOT NULL,
    occupied INTEGER NOT NULL
    );
  ''')

    conn.commit()
    conn.close()

    return {"message": "Database initialized"}

from flask import request

#Doctors API
@app.route('/doctors', methods=['POST'])
def add_doctor():
    data = request.json

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO doctors (name, specialization, fees) VALUES (?, ?, ?)",
        (data['name'], data['specialization'], data['fees'])
    )

    conn.commit()
    conn.close()

    return {"message": "Doctor added successfully"}

@app.route('/doctors', methods=['GET'])
def get_doctors():
    conn = get_db_connection()
    doctors = conn.execute("SELECT * FROM doctors").fetchall()
    conn.close()

    return jsonify([dict(row) for row in doctors])

@app.route('/doctors/<int:id>', methods=['DELETE'])
def delete_doctor(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM doctors WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return {"message": "Doctor deleted"}

#Patients API
@app.route('/patients', methods=['POST'])
def add_patient():
    data = request.json

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO patients (name, age, disease, contact) VALUES (?, ?, ?, ?)",
        (data['name'], data['age'], data['disease'], data['contact'])
    )

    conn.commit()
    conn.close()

    return {"message": "Patient added successfully"}

@app.route('/patients', methods=['GET'])
def get_patients():
    conn = get_db_connection()
    patients = conn.execute("SELECT * FROM patients").fetchall()
    conn.close()

    return jsonify([dict(row) for row in patients])

@app.route('/patients/<int:id>', methods=['DELETE'])
def delete_patient(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM patients WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return {"message": "Patient deleted"}

#Appointments API
@app.route('/appointments', methods=['POST'])
def add_appointment():
    data = request.json

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO appointments (patient_id, doctor_id, date, time) VALUES (?, ?, ?, ?)",
        (data['patient_id'], data['doctor_id'], data['date'], data['time'])
    )

    conn.commit()
    conn.close()

    return {"message": "Appointment booked"}


@app.route('/appointments', methods=['GET'])
def get_appointments():
    conn = get_db_connection()

    appointments = conn.execute('''
        SELECT a.id, p.name as patient, d.name as doctor, a.date, a.time
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors d ON a.doctor_id = d.id
    ''').fetchall()

    conn.close()

    return jsonify([dict(row) for row in appointments])

@app.route('/appointments/<int:id>', methods=['DELETE'])
def delete_appointment(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM appointments WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return {"message": "Appointment deleted"}

#Dashboard
@app.route('/dashboard', methods=['GET'])
def dashboard():
    conn = get_db_connection()

    doctors = conn.execute("SELECT COUNT(*) FROM doctors").fetchone()[0]
    patients = conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
    appointments = conn.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]
    wards = conn.execute("SELECT COUNT(*) FROM wards").fetchone()[0]

    recent = conn.execute('''
        SELECT p.name as patient, d.name as doctor, a.date, a.time
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors d ON a.doctor_id = d.id
        ORDER BY a.id DESC
        LIMIT 5
    ''').fetchall()

    conn.close()

    return jsonify({
        "doctors": doctors,
        "patients": patients,
        "appointments": appointments,
        "recent": [dict(r) for r in recent],
        "wards": wards
    })

#Edit Feature
@app.route('/patients/<int:id>', methods=['PUT'])
def update_patient(id):
    data = request.json

    conn = get_db_connection()
    conn.execute(
        "UPDATE patients SET name=?, age=?, disease=?, contact=? WHERE id=?",
        (data['name'], data['age'], data['disease'], data['contact'], id)
    )
    conn.commit()
    conn.close()

    return {"message": "Patient updated"}

@app.route('/doctors/<int:id>', methods=['PUT'])
def update_doctor(id):
    data = request.json

    conn = get_db_connection()
    conn.execute(
        "UPDATE doctors SET name=?, specialization=?, fees=? WHERE id=?",
        (data['name'], data['specialization'], data['fees'], id)
    )
    conn.commit()
    conn.close()

    return {"message": "Doctor updated"}

@app.route('/appointments/<int:id>', methods=['PUT'])
def update_appointment(id):
    data = request.json

    conn = get_db_connection()
    conn.execute(
        "UPDATE appointments SET date=?, time=? WHERE id=?",
        (data['date'], data['time'], id)
    )
    conn.commit()
    conn.close()

    return {"message": "Appointment updated"}


#Ward API
@app.route('/wards', methods=['GET'])
def get_wards():
    conn = get_db_connection()
    wards = conn.execute("SELECT * FROM wards").fetchall()
    conn.close()

    return jsonify([dict(w) for w in wards])

@app.route('/wards', methods=['POST'])
def add_ward():
    data = request.json

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO wards (name, capacity, occupied) VALUES (?, ?, ?)",
        (data['name'], data['capacity'], data['occupied'])
    )
    conn.commit()
    conn.close()

    return {"message": "Ward added"}

if __name__ == '__main__':
    app.run(debug=True)