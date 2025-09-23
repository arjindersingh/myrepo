from django.shortcuts import render, get_object_or_404, redirect
from accounts.models.academicyear import AcademicYear
from appraisal.models.appraisal_type import AppraisalSchedule, AppraisalType
from appraisal.forms.appraisal_schedule import AppraisalScheduleForm
from accounts.context_processors import current_academic_year


def appraisal_schedule_list(request, appraisal_type_id):
    appraisal_type = get_object_or_404(AppraisalType, id=appraisal_type_id)
    CAY = current_academic_year()  # AcademicYear object

    schedules = AppraisalSchedule.objects.filter(
        academic_year=CAY.id,  # filter by ID
        appraisal_type=appraisal_type
    ).order_by('-created_date')
    print (schedules)
    return render(request, 'appraisal_schedule/list.html', {
        'appraisal_type': appraisal_type,
        'schedules': schedules,
        'CAY': CAY
    })

def appraisal_schedule_add(request, appraisal_type_id):
    CAY = current_academic_year()  # Already an AcademicYear instance
    appraisal_type = get_object_or_404(AppraisalType, id=appraisal_type_id)

    if request.method == "POST":
        form = AppraisalScheduleForm(request.POST)
        if form.is_valid():
            schedule_obj = form.save(commit=False)
            schedule_obj.academic_year = CAY
            schedule_obj.appraisal_type = appraisal_type
            schedule_obj.save()
            return redirect('appraisal_type_list')
    else:
        form = AppraisalScheduleForm()

    return render(
        request,
        'appraisal_schedule/add.html',
        {
            'form': form,
            'appraisal_type': appraisal_type,
            'CAY': CAY,
            'is_edit': False
        }
    )



def appraisal_schedule_edit(request, schedule_id):
    CAY = current_academic_year()

    # Always fetch an existing schedule for editing
    schedule = get_object_or_404(AppraisalSchedule, id=schedule_id)
    appraisal_type = schedule.appraisal_type

    if request.method == "POST":
        form = AppraisalScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            return redirect('appraisal_type_list')  # Redirect after update
    else:
        form = AppraisalScheduleForm(instance=schedule)

    return render(request, 'appraisal_schedule/edit.html', {
        'form': form,
        'appraisal_type': appraisal_type,
        'CAY': CAY
    })


def appraisal_schedule_delete(request, schedule_id):
    schedule = get_object_or_404(AppraisalSchedule, id=schedule_id)
    if request.method == "POST":
        schedule.delete()
        return redirect('appraisal_type_list')
    return redirect('appraisal_type_list')
