from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import uuid4

app = FastAPI(title="Student API", description="Simple CRUD API for Student Data")


# Pydantic Model for Student
class Student(BaseModel):
    id: Optional[str] = None
    name: str = Field(..., min_length=1, description="Student name")
    age: int = Field(..., gt=0, le=120, description="Student age")
    grade: str = Field(..., min_length=1, description="Student grade/class")
    email: str = Field(..., description="Student email")


# In-memory database
students_db: List[Student] = []


# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Student API", "docs": "/docs", "total_students": len(students_db)}


# Create - Add a new student
@app.post("/students/", response_model=Student, status_code=201)
async def create_student(student: Student):
    """Create a new student"""
    student.id = str(uuid4())
    students_db.append(student)
    return student


# Read - Get all students
@app.get("/students/", response_model=List[Student])
async def get_all_students():
    """Get all students"""
    return students_db


# Read - Get a specific student by ID
@app.get("/students/{student_id}", response_model=Student)
async def get_student(student_id: str):
    """Get a student by ID"""
    for student in students_db:
        if student.id == student_id:
            return student
    raise HTTPException(status_code=404, detail="Student not found")


# Update - Update a student
@app.put("/students/{student_id}", response_model=Student)
async def update_student(student_id: str, updated_student: Student):
    """Update a student by ID"""
    for index, student in enumerate(students_db):
        if student.id == student_id:
            updated_student.id = student_id
            students_db[index] = updated_student
            return updated_student
    raise HTTPException(status_code=404, detail="Student not found")


# Delete - Remove a student
@app.delete("/students/{student_id}", status_code=204)
async def delete_student(student_id: str):
    """Delete a student by ID"""
    for index, student in enumerate(students_db):
        if student.id == student_id:
            students_db.pop(index)
            return
    raise HTTPException(status_code=404, detail="Student not found")


# Search students by name
@app.get("/students/search/", response_model=List[Student])
async def search_students(name: str):
    """Search students by name"""
    results = [s for s in students_db if name.lower() in s.name.lower()]
    return results
