from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.db import transaction

from appraisal.forms.emp_selection_setting import EmpSelectionSettingsForm
from accounts.models.academicyear import AcademicYear
from appraisal.models.appraisal_type import AppraisalType, EmpSelectionCriteria, EmpSelectionData
from accounts.context_processors import current_academic_year


@transaction.atomic
def emp_selection_settings_for_appraisal_type(request, appraisal_type_id):
    CAT = get_object_or_404(AppraisalType, pk=appraisal_type_id)  # CAT
    #CAY = current_academic_year()                             # CAY

    # 1) Load all criteria
    criteria_qs = EmpSelectionCriteria.objects.all().order_by("display_name", "name")

    # 2) Read existing EmpSelectionData for CAT + CAY
    existing_map = {
        esd.emp_selection_criteria_id: esd
        for esd in EmpSelectionData.objects.filter(
            appraisal_type=CAT
        )
    }

    # 3) Build initial values: existing value if present; else default_value
    initial_values = {
        crit.pk: existing_map.get(crit.pk).value if existing_map.get(crit.pk) is not None else crit.default_value
        for crit in criteria_qs
    }

    if request.method == "POST":
        form = EmpSelectionSettingsForm(request.POST, criteria_qs=criteria_qs, initial_values=initial_values)
        if form.is_valid():
            # 5) Save (upsert) to EmpSelectionData
            saved = 0
            for crit in criteria_qs:
                field_name = f"crit_{crit.pk}"
                new_value = form.cleaned_data[field_name]

                obj = existing_map.get(crit.pk)
                if obj is None:
                    obj = EmpSelectionData(
                        appraisal_type=CAT,
                        emp_selection_criteria=crit,
                    )
                obj.value = new_value
                # Keep description synced with master description (or customize as needed)
                obj.description = "Employee Selection Description"
                obj.save()
                saved += 1

            messages.success(request, f"Settings saved for {saved} criteria.")
            return redirect("emp_selection_settings_for_appraisal_type", appraisal_type_id=CAT.pk)
    else:
        form = EmpSelectionSettingsForm(criteria_qs=criteria_qs, initial_values=initial_values)

    context = {
        "form": form,
        "criteria_qs": criteria_qs,
        "CAT": CAT,
        "page_title": "Employee Selection Settings",
    }
    return render(request, "appraisal_type/emp_selection_setting.html", context)
