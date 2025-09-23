# appraisal/views.py
from django.shortcuts import render, get_object_or_404, redirect
from appraisal.models.appraisal_type import AppraisalType
from appraisal.forms.appraisal_type import AppraisalTypeForm

# List Appraisal Types
def appraisal_type_list(request):
    appraisal_types = AppraisalType.objects.all()
    return render(request, 'appraisal_type/list.html', {'appraisal_types': appraisal_types})

# Create Appraisal Type
def appraisal_type_create(request):
    if request.method == "POST":
        form = AppraisalTypeForm(request.POST)
        if form.is_valid():
            # Save the AppraisalType instance without committing to the database
            appraisal_type = form.save(commit=False)
            # Save the instance to the database
            appraisal_type.save()
            # Now save the ManyToManyField relationships
            form.save_m2m()
            return redirect('appraisal_type_list')
        else:
            # Debugging: Print form errors to understand why the form is invalid
            print(form.errors)
    else:
        form = AppraisalTypeForm()
    return render(request, 'appraisal_type/add_edit.html', {'form': form, 'title': 'Add Appraisal Type'})

# Edit Appraisal Type
def appraisal_type_edit(request, pk):
    appraisal_type = get_object_or_404(AppraisalType, pk=pk)
    if request.method == "POST":
        form = AppraisalTypeForm(request.POST, instance=appraisal_type)
        if form.is_valid():
            form.save()
            return redirect('appraisal_type_list')
    else:
        form = AppraisalTypeForm(instance=appraisal_type)
    return render(request, 'appraisal_type/add_edit.html', {'form': form, 'title': 'Edit Appraisal Type'})

# View Details
def appraisal_type_detail(request, pk):
    appraisal_type = get_object_or_404(AppraisalType, pk=pk)
    return render(request, 'appraisal_type/detail.html', {'appraisal_type': appraisal_type})

# Schedule List for a given Appraisal Type
""" def appraisal_schedule_list(request, appraisal_type_id):
    appraisal_type = get_object_or_404(AppraisalType, id=appraisal_type_id)
    schedules = AppraisalSchedule.objects.filter(appraisal_type=appraisal_type)
    return render(request, 'appraisal_type/schedule_list.html', {
        'appraisal_type': appraisal_type,
        'schedules': schedules
    }) """

# Appriasal Type Delete 
def appraisal_type_delete(request, atype_id):
    appraisal_type = get_object_or_404(AppraisalType, id=atype_id)
    appraisal_type.delete()
    return redirect('appraisal_type_list')