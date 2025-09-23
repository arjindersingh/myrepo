from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from accounts.decorators import menu_permission_required
from accounts.models.employee import Employee
from accounts.forms.employee import EmployeeForm

# List all employees
@menu_permission_required
def list_employees(request):
    employees = Employee.objects.all()
    return render(request, 'employee/list.html', {'employees': employees})

# Create a new employee
def create_employee(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_employees')
    else:
        form = EmployeeForm()
    return render(request, 'employee/add_edit.html', {'form': form})

# View details of a single employee
def view_employee_detail(request, emp_id):
    employee = get_object_or_404(Employee, id=emp_id)
    return render(request, 'employee/detail.html', {'employee': employee})

# Update an existing employee
def edit_employee(request, emp_id):
    employee = get_object_or_404(Employee, id=emp_id)
    if request.method == "POST":
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('list_employees')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'employee/add_edit.html', {'form': form})

# Delete an employee
def delete_employee(request, emp_id):
    employee = get_object_or_404(Employee, id=emp_id)
    if request.method == "POST":
        employee.delete()
        return redirect('list_employees')
    return render(request, 'employee/confirm_delete.html', {'employee': employee})
