from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 1. Configure SQLite Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smartcare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 2. Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    med_name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False)  # e.g., '08:00 AM'
    status = db.Column(db.String(20), default='PENDING')  # 'PENDING', 'TAKEN', 'MISSED'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# 3. Create database tables automatically
with app.app_context():
    db.create_all()

# 4. API Endpoints with all 4 HTTP Methods

@app.route('/')
def home():
    return render_template('index.html')

# POST: Add a new user
@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    new_user = User(username=data['username'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": f"User {data['username']} created successfully!"})

# POST: Add a new prescription
@app.route('/add_prescription', methods=['POST'])
def add_prescription():
    data = request.json
    new_prescription = Prescription(
        med_name=data['med_name'],
        dosage=data['dosage'],
        time=data['time'],
        user_id=data['user_id']
    )
    db.session.add(new_prescription)
    db.session.commit()
    return jsonify({"message": f"Prescription for {data['med_name']} added successfully!"})

# GET: Fetch all prescriptions for a specific user
@app.route('/get_prescriptions/<int:user_id>', methods=['GET'])
def get_prescriptions(user_id):
    prescriptions = Prescription.query.filter_by(user_id=user_id).all()
    result = []
    for p in prescriptions:
        result.append({
            "id": p.id,
            "med_name": p.med_name,
            "dosage": p.dosage,
            "time": p.time,
            "status": p.status
        })
    return jsonify(result)

# PUT: Update prescription details or adherence status
@app.route('/update_prescription/<int:prescription_id>', methods=['PUT'])
def update_prescription(prescription_id):
    data = request.json
    prescription = Prescription.query.get_or_404(prescription_id)
    prescription.med_name = data.get('med_name', prescription.med_name)
    prescription.dosage = data.get('dosage', prescription.dosage)
    prescription.time = data.get('time', prescription.time)
    prescription.status = data.get('status', prescription.status)
    db.session.commit()
    return jsonify({"message": f"Prescription {prescription_id} updated successfully!"})

# DELETE: Remove a prescription
@app.route('/delete_prescription/<int:prescription_id>', methods=['DELETE'])
def delete_prescription(prescription_id):
    prescription = Prescription.query.get_or_404(prescription_id)
    db.session.delete(prescription)
    db.session.commit()
    return jsonify({"message": f"Prescription {prescription_id} deleted successfully!"})

if __name__ == '__main__':
    app.run(debug=True)
