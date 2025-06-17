from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app = Flask(__name__)

# Replace with your actual MySQL credentials
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Ilovemessi2022!@localhost/mydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Employee(db.Model):
    __tablename__ = 'employees' # This is crucial and you already added it!

    # Map 'employee_id' from your DB to 'employee_id' in your model
    employee_id = db.Column(db.Integer, primary_key=True)

    # Map 'first_name' from your DB to 'first_name' in your model
    first_name = db.Column(db.String(100), nullable=False)

    # Map 'last_name' from your DB to 'last_name' in your model
    last_name = db.Column(db.String(100), nullable=False)

    # Map 'hourly_pay' from your DB
    hourly_pay = db.Column(db.Float) # Use db.Float or db.Numeric

    # Map 'hire_date' from your DB
    hire_date = db.Column(db.Date) # Use db.Date for date type

    def __repr__(self):
        return f'<Employee {self.first_name} {self.last_name}>'

    def to_dict(self):
        return {
            'employee_id': self.employee_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'hourly_pay': self.hourly_pay,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None
        }
    
@app.route('/')
def index():
    employees = Employee.query.all()
    for emp in employees:
        print(f"{emp.employee_id} - {emp.first_name}")
    return "Printed all employees in terminal."

@app.route('/')
def hello():
    return 'Hello, World!'
    

if __name__ == '__main__':
    app.run(debug=True)

