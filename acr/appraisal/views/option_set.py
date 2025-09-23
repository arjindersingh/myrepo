from django.shortcuts import render, redirect, get_object_or_404
from accounts.decorators import menu_permission_required
from appraisal.models.scale import OptionSet
from appraisal.forms.optionset import OptionSetForm

@menu_permission_required
def list_option_set(request):
    """View to list all option sets."""
    option_sets = OptionSet.objects.all()
    return render(request, 'scale/list_option_set.html', {'option_sets': option_sets})

def add_option_set(request):
    """View to add a new option set."""
    if request.method == 'POST':
        form = OptionSetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('option_set_list')  # Redirect to list view
    else:
        form = OptionSetForm()
    
    return render(request, 'scale/add_option_set.html', {'form': form, 'action': 'Add'})
