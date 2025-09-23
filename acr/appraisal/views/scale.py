from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from accounts.decorators import menu_permission_required
from appraisal.forms.scale import ScaleForm
from appraisal.models.scale import Scale

# View to list all scales with dimensions and items
@menu_permission_required
def scale_list(request):
    scales = Scale.objects.all()
    return render(request, 'scale/list.html', {'scales': scales})

# View to create a complete scale with related dimensions, items, and options

def add_scale(request):
    if request.method == "POST":
        form = ScaleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Scale added successfully!")
            return redirect('show_scale_list')  # Redirect to scale list after adding
    else:
        form = ScaleForm()

    return render(request, 'scale/add_scale.html', {'form': form})

def edit_scale(request, pk):
    scale = get_object_or_404(Scale, pk=pk)
    if request.method == 'POST':
        form = ScaleForm(request.POST, instance=scale)
        if form.is_valid():
            form.save()
            return redirect('show_scale_list')
    else:
        form = ScaleForm(instance=scale)
    return render(request, 'scale/edit_scale.html', {'form': form, 'scale': scale})