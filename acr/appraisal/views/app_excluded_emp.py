from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from appraisal.forms.app_exclude_emp import AppExcludedEmpCreateForm
from accounts.models.academicyear import AcademicYear
from appraisal.models.appraisal_type import AppraisalType
from appraisal.models.app_excluded_emp import AppExcludedEmp
from accounts.models.employee import Employee
from accounts.context_processors import current_academic_year
from django.db import IntegrityError

@login_required
def manage_app_excluded_emps(request):
    """Page with:
      - Search box (AJAX) to find Employee by name or emp_code
      - Add selected to AppExcludedEmp for CAY + CU (+ appraisal_type if provided)
      - List CAY+CU exclusions with delete buttons
    Optional: pass ?appraisal_type=<id> to scope by appraisal type.
    """
    CAY =   current_academic_year()

    if request.method == "POST":
        form = AppExcludedEmpCreateForm(
            request.POST,
            current_user=request.user,
            current_ay=CAY,
        )
        if form.is_valid():
            try:
                entry = form.save()  # user & academic_year set in form.save()
                messages.success(request, f"{entry.ex_employee} added to exclusions.")
                return redirect(request.get_full_path())
            except IntegrityError as e:
                messages.error(request, "This employee is already excluded for the selected appraisal type.")
            except Exception as e:
                messages.error(request, f"Could not add: {e}")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = AppExcludedEmpCreateForm(current_user=request.user, current_ay=CAY)

    # Listing
    #qs = AppExcludedEmp.objects.filter(user=request.user, academic_year=CAY)
    qs = AppExcludedEmp.objects.filter(
        user=request.user,
        academic_year=CAY
        ).select_related("ex_employee", "appraisal_type")

    """ if appraisal_type:
        qs = qs.filter(appraisal_type=appraisal_type)
    qs = qs.select_related("ex_employee", "appraisal_type").order_by("ex_employee__emp_name")
 """
    context = {
        "form": AppExcludedEmpCreateForm(),
        "exclusions": qs,
        "CAY": CAY,
    }
    return render(request, "process/app_exclude_emp.html", context)


@login_required
def app_ex_employee_lookup(request):
    """
    JSON endpoint for autocomplete. Query by emp_name or emp_code.
    GET params:
      q: search string
      limit: optional result cap (default 15)
    """
    q = (request.GET.get("q") or "").strip()
    limit = int(request.GET.get("limit") or 15)
    qs = Employee.objects.all()
    if q:
        qs = qs.filter(
            Q(emp_name__icontains=q) | Q(emp_code__icontains=q)
        )
    qs = qs.order_by("emp_name")[:limit]

    results = [
        {
            "id": e.id,
            "emp_name": e.emp_name,
            "emp_code": getattr(e, "emp_code", ""),
            "label": f"{e.emp_name} ({getattr(e, 'emp_code', '')})".strip(),
        }
        for e in qs
    ]
    return JsonResponse({"results": results})


@login_required
@require_POST
def delete_app_excluded_emp(request, pk):
    """
    Delete one record if it belongs to current user and current AY.
    """
    cay = current_academic_year()
    entry = get_object_or_404(AppExcludedEmp, pk=pk, user=request.user, academic_year=cay)
    entry.delete()
    messages.success(request, "Removed from Apprisal Excluded Employee List.")
    # return to same page (preserve appraisal_type filter if present)
    return redirect(request.META.get("HTTP_REFERER") or "excluded-manage")
