from flask import Flask,request,jsonify
from pymongo import MongoClient
from uuid import uuid4
app = Flask(__name__)
client = MongoClient("mongodb+srv://guffranjgshaik_db_user:zFMHm7NoVSVvHUky@studentattendance.u8cdbrl.mongodb.net/?appName=StudentAttendance")
studentdb = client["student_data"]
studentassignmentcollection = studentdb["Personal_info"]

@app.post("/students")
def add_student():
    data = request.get_json()
    student = studentassignmentcollection.find_one({"email":data["email"]})
    if student:
        return "Student already exists"
    student = {
        "id":str(uuid4()),
        "name":data["name"],
        "email":data["email"],
        "course":data["course"],
        "assignments":[]
    }
    studentassignmentcollection.insert_one(student)
    return "Student added"

@app.get("/students")
def get_students():
    students = list(studentassignmentcollection.find())
    for student in students:
        student["_id"] = str(student["_id"])
    return students

@app.post("/students/<student_id>/assignments")
def add_assignment(student_id):
    data = request.get_json()
    student = studentassignmentcollection.find_one({"id":student_id})
    if not student:
        return "Student not found"
    assignment = {
        "title":data["title"],
        "score":data["score"]
    }
    studentassignmentcollection.update_one(
        {"id":student_id},
        {"$push":{"assignments":assignment}}
    )
    return "Assignment added"

@app.get("/students/top-performers/<int:score>")
def get_top_performers(score):
    students = list(studentassignmentcollection.find({
        "assignments.score":{"$gte":score}
    }))
    for student in students:
        student["_id"] = str(student["_id"])
    return students

@app.get("/students/<student_id>/average-score")
def get_average_score(student_id):
    student = studentassignmentcollection.find_one({"id":student_id})
    if not student:
        return "Student not found"
    assignments = student["assignments"]
    total = 0
    for assignment in assignments:
        total += assignment["score"]
    average = total / len(assignments)
    return jsonify({
        "student":student["name"],
        "average_score":round(average,2)
    })

if __name__ == "__main__":
    app.run(debug=True)
