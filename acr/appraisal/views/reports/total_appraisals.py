from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from accounts.context_processors import current_academic_year
from accounts.models.institute import Institute
from accounts.models.employee import JobCategory
from appraisal.models.appraisal_data import TotalAppraisalData


@login_required
def list_total_appraisals(request):
    CAY = current_academic_year()

    # Filters
    institute_id = request.GET.get('institute')
    jobcat_id = request.GET.get('jobcat')
    q = request.GET.get('q', '').strip()

    qs = TotalAppraisalData.objects.filter(appraisal_year=CAY)

    if institute_id:
        qs = qs.filter(emp_institute_id=institute_id)
    if jobcat_id:
        qs = qs.filter(emp_job_category_id=jobcat_id)

    # Search across employee name/code
    if q:
        qs = qs.filter(employee__emp_name__icontains=q) | qs.filter(employee__emp_code__icontains=q)

    # Group by employee: choose latest appraisal_no per employee and aggregate scores
    # We'll collect per-employee list of total records ordered by appraisal_no desc
    employees = {}
    for t in qs.select_related('employee', 'appraisal_type').order_by('employee', '-appraisal_no'):
        emp_id = t.employee_id
        employees.setdefault(emp_id, {
            'employee': t.employee,
            'records': [],
            'total_max': 0,
            'total_obt': 0,
        })
        employees[emp_id]['records'].append(t)
        employees[emp_id]['total_max'] += t.max_score
        employees[emp_id]['total_obt'] += t.obt_score

    # Convert to list
    grouped = list(employees.values())

    institutes = Institute.objects.all()
    jobcats = JobCategory.objects.all()

    return render(request, 'reports/total_appraisals.html', {
        'grouped': grouped,
        'institutes': institutes,
        'jobcats': jobcats,
        'selected_institute': institute_id,
        'selected_jobcat': jobcat_id,
        'q': q,
        'CAY': CAY,
    })


@login_required
def delete_total_appraisal(request, pk):
    # delete a TotalAppraisalData record
    obj = get_object_or_404(TotalAppraisalData, pk=pk)
    if request.method == 'POST':
        obj.delete()
        return redirect('total_appraisals')
    return render(request, 'reports/confirm_delete.html', {'object': obj})
