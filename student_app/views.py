from django.contrib import messages



from django.contrib.auth.decorators import login_required

from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import StudentForm,CustomUserCreationForm
from .models import Student

# REGISTRATION VIEW
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            messages.success(request, f"Welcome , {user.first_name}!")
            return redirect('student_app:list')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {
        'form': form
    })

# 1. LIST VIEW (With Search)
@login_required
def student_list(request):
    query = request.GET.get('q', '')
    if query:
        students = Student.objects.filter(
            Q(name__icontains=query) | Q(email__icontains=query)
        )
    else:
        students = Student.objects.all().order_by('-created_at')
        
    return render(request, 'student_app/student_list.html', {
        'students': students,
        'query': query
    })

# 2. DETAIL VIEW
@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'student_app/student_detail.html', {'student': student})

# 3. CREATE VIEW
@login_required
def student_add(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(request, f"Student '{student.name}' was successfully added!")
            return redirect('student_app:list')
    else:
        form = StudentForm()
        
    return render(request, 'student_app/student_form.html', {
        'form': form,
        'title': 'Add New Student',
        'button_text': 'Save Student'
    })

# 4. UPDATE VIEW
@login_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f"Student '{student.name}' was successfully updated!")
            return redirect('student_app:detail', pk=student.pk)
    else:
        form = StudentForm(instance=student)
        
    return render(request, 'student_app/student_form.html', {
        'form': form,
        'student': student,
        'title': f'Edit Student: {student.name}',
        'button_text': 'Update Student'
    })

# 5. DELETE VIEW
@login_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        name = student.name
        student.delete()
        messages.success(request, f"Student '{name}' was deleted.")
        return redirect('student_app:list')
        
    return render(request, 'student_app/student_confirm_delete.html', {'student': student})
