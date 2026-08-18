from django.shortcuts import render
from django.http import HttpResponse, Http404

# Create your views here.
STUDENTS = {
    1: {"name": "John Doe", "age": 20, "course": "Computer Science", "marks": 85},
    2: {"name": "Jane Smith", "age": 22, "course": "Mathematics", "marks": 90},
    3: {"name": "Mike Johnson", "age": 21, "course": "Physics", "marks": 78},
}


def student_list(request):
    html = "<h1>All students</h1><ul>"
    for pk, s in STUDENTS.items():
        html += f'<li><a href="/students/{pk}/">{s["name"]}</a></li>'
        html += "</ul>"
        return HttpResponse(html)


def student_detail(request, pk):
    student = STUDENTS.get(pk)
    if not student:
        raise Http404("Student not found")
    return HttpResponse(f"""
        <h1>{student['name']}</h1>
        <p>Course: {student['course']}</p>
        <p>Marks: {student['marks']}%</p>
        <a href="/students/"> back to list</a>""")
