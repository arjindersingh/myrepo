from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from accounts.context_processors import current_academic_year
from django.db.models import Max
from accounts.models.academicyear import AcademicYear
from accounts.models.employee import Employee, JobCategory
from accounts.models.institute import Institute
from appraisal.models.appraisal_type import AppraisalType
from appraisal.models.scale import Scale, Item
from appraisal.models.appraisal_data import AppraisalDataItemWise, TotalAppraisalData  # adjust import if needed


@login_required
#@menu_permission_required
def show_appraisal_form(request, appraisal_type_id, employee_id):
    CAT = get_object_or_404(AppraisalType, pk=appraisal_type_id)
    employee = get_object_or_404(Employee, pk=employee_id)
    CAT_scale = get_object_or_404(Scale, id=CAT.scale.id)

    # Allowed choices for this employee
    emp_institutes = employee.institutes.all()
    if not emp_institutes:
        messages.error(request, "Current employee does not belong to any institute. Contact administrator.")
        return redirect('start_appraisal_process', appraisal_type_id=appraisal_type_id)
    emp_job_category = employee.job_categories.all()
    if not emp_job_category:
        messages.error(request, "Current employee does not belong to any Job Category. Contact administrator.")
        return redirect('start_appraisal_process', appraisal_type_id=appraisal_type_id)

    # ✅ Current Academic Year
    CAY = current_academic_year()
    if not CAY:
        messages.error(request, "Current Academic Year is not available. Contact administrator.")
        return redirect("show_appraisal_dashboard")

    # Defaults (first available) for GET
    default_inst_id = emp_institutes.first().id if emp_institutes.exists() else None
    default_jc_id = emp_job_category.first().id if emp_job_category.exists() else None

    # Read selection from POST (or keep defaults on GET)
    selected_emp_institute_id = request.POST.get("emp_institutes") or default_inst_id
    selected_emp_job_category_id = request.POST.get("emp_job_categories") or default_jc_id

    if request.method == "POST":
        # Validate selections exist
        try:
            inst_id = int(selected_emp_institute_id) if selected_emp_institute_id is not None else None
            jc_id = int(selected_emp_job_category_id) if selected_emp_job_category_id is not None else None
        except (TypeError, ValueError):
            inst_id = jc_id = None

        allowed_inst_ids = set(emp_institutes.values_list("id", flat=True))
        allowed_jc_ids = set(emp_job_category.values_list("id", flat=True))

        if not inst_id or not jc_id or inst_id not in allowed_inst_ids or jc_id not in allowed_jc_ids:
            messages.error(request, "Please select a valid Institute and Job Category for this employee.")
            context = {
                "CAT": CAT,
                "employee": employee,
                "CAT_scale": CAT_scale,
                "CAY": CAY,
                "filled_answers": {},
                "remarks_filled": request.POST.get("remarks", "").strip(),
                "emp_institutes": emp_institutes,
                "emp_job_categories": emp_job_category,
                "selected_emp_institute_id": selected_emp_institute_id,
                "selected_emp_job_category_id": selected_emp_job_category_id,
            }
            return render(request, "process/show_app_form.html", context)

        selected_inst = get_object_or_404(Institute, pk=inst_id)
        selected_jc = get_object_or_404(JobCategory, pk=jc_id)

        unanswered_items = []
        answers = {}

        # Collect answers
        for item in CAT_scale.items.all():
            field_name = f"item_{item.id}"
            value = request.POST.get(field_name)
            if value in (None, ""):
                unanswered_items.append(item.statement)
            else:
                answers[item] = int(value)

        # If any unanswered → error
        if unanswered_items:
            messages.error(
                request,
                f"You must answer all items before submitting. Unanswered: {len(unanswered_items)} item(s)."
            )
            context = {
                "CAT": CAT,
                "employee": employee,
                "CAT_scale": CAT_scale,
                "CAY": CAY,
                "filled_answers": {f"item_{item.id}": str(val) for item, val in answers.items()},
                "remarks_filled": request.POST.get("remarks", "").strip(),
                "emp_institutes": emp_institutes,
                "emp_job_categories": emp_job_category,
                "selected_emp_institute_id": selected_emp_institute_id,
                "selected_emp_job_category_id": selected_emp_job_category_id,
            }
            return render(request, "process/show_app_form.html", context)

        try:
            with transaction.atomic():
                # Compute next appraisal_no from TOTAL table (single source of truth)
                last_no = (
                    TotalAppraisalData.objects
                    .filter(appraisal_year=CAY, appraisal_type=CAT, employee=employee)
                    .aggregate(mx=Max("appraisal_no"))["mx"]
                )
                next_no = 1 if last_no is None else last_no + 1

                total_max_scores = 0
                total_obt_scores = 0

                # Save item-wise (if your model has institute/category fields, add them there too)
                for item, value in answers.items():
                    MS = item.max_option_value if value != 0 else 0
                    total_max_scores += MS
                    total_obt_scores += value

                    AppraisalDataItemWise.objects.create(
                        appraisal_year=CAY,
                        appraisal_type=CAT,
                        employee=employee,
                        appraisal_no=next_no,  # same number for all items
                        item=item,
                        max_score=MS,
                        obt_score=value,
                        user=request.user if request.user.is_authenticated else None,
                        emp_institute=selected_inst,         # uncomment if field exists
                        emp_job_category=selected_jc,        # uncomment if field exists
                    )

                # Save total appraisal WITH institute & job category ✅
                remarks = request.POST.get("remarks", "").strip()
                TotalAppraisalData.objects.create(
                    appraisal_year=CAY,
                    appraisal_type=CAT,
                    employee=employee,
                    emp_institute=selected_inst,
                    emp_job_category=selected_jc,
                    appraisal_no=next_no,
                    user=request.user if request.user.is_authenticated else None,
                    max_score=total_max_scores,
                    obt_score=total_obt_scores,
                    remarks=remarks
                )

            messages.success(
                request,
                f"The Appraisal {CAT.display_name} for Employee {employee.emp_name} is saved. Fill another."
            )
            return redirect("start_appraisal_process", appraisal_type_id=appraisal_type_id)

        except Exception as e:
            messages.error(request, f"Error occurred while saving appraisal: {str(e)}")
            return redirect("show_appraisal_dashboard")

    # Normal GET response
    context = {
        "CAT": CAT,
        "employee": employee,
        "CAT_scale": CAT_scale,
        "CAY": CAY,
        "filled_answers": {},
        "remarks_filled": "",
        "emp_institutes": emp_institutes,
        "emp_job_categories": emp_job_category,
        "selected_emp_institute_id": selected_emp_institute_id,
        "selected_emp_job_category_id": selected_emp_job_category_id,
    }
    return render(request, "process/show_app_form.html", context)