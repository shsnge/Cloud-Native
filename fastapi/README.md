# Student API - FastAPI CRUD Application

Simple FastAPI application for managing student data with CRUD operations.

## Features

- Create new student
- Get all students
- Get student by ID
- Update student
- Delete student
- Search students by name

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Run the Server

```bash
uvicorn main:app --reload
```

Or using FastAPI CLI:
```bash
fastapi dev main.py
```

Server will run at: **http://localhost:8000**

## API Documentation

Once server is running, open:
- Swagger UI: **http://localhost:8000/docs**
- ReDoc: **http://localhost:8000/redoc**

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint |
| GET | `/students/` | Get all students |
| GET | `/students/{id}` | Get student by ID |
| GET | `/students/search/?name=` | Search students by name |
| POST | `/students/` | Create new student |
| PUT | `/students/{id}` | Update student |
| DELETE | `/students/{id}` | Delete student |

## Student Data Model

```json
{
  "id": "auto-generated",
  "name": "string",
  "age": "integer (1-120)",
  "grade": "string",
  "email": "string"
}
```

## Example Requests

### Create a Student
```bash
curl -X POST "http://localhost:8000/students/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ali Khan",
    "age": 20,
    "grade": "BS-CS-1",
    "email": "ali@example.com"
  }'
```

### Get All Students
```bash
curl -X GET "http://localhost:8000/students/"
```

### Get Student by ID
```bash
curl -X GET "http://localhost:8000/students/{student_id}"
```

### Update Student
```bash
curl -X PUT "http://localhost:8000/students/{student_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ali Khan",
    "age": 21,
    "grade": "BS-CS-2",
    "email": "ali.updated@example.com"
  }'
```

### Delete Student
```bash
curl -X DELETE "http://localhost:8000/students/{student_id}"
```

### Search Students
```bash
curl -X GET "http://localhost:8000/students/search/?name=ali"
```

## Project Structure

```
fastapi/
├── main.py            # Main application file
├── requirements.txt   # Python dependencies
└── README.md          # This file
```
