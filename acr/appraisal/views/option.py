from django.shortcuts import render, redirect, get_object_or_404
from appraisal.models.scale import OptionSet, Option
from appraisal.forms.option import OptionForm

def add_option(request, option_set_id):
    """View to add an option to a specific option set."""
    option_set = get_object_or_404(OptionSet, id=option_set_id)

    if request.method == 'POST':
        form = OptionForm(request.POST)
        if form.is_valid():
            option = form.save(commit=False)
            option.option_set = option_set
            option.save()
            return redirect('option_set_list')  # Redirect to OptionSet list
    else:
        form = OptionForm()

    return render(request, 'scale/add_option.html', {'form': form, 'option_set': option_set, 'action': 'Add'})


def edit_option(request, option_id):
    option = get_object_or_404(Option, id=option_id)
    option_set = option.option_set  # Retrieve related OptionSet

    if request.method == "POST":
        form = OptionForm(request.POST, instance=option)
        if form.is_valid():
            form.save()
            return redirect('add_option', option_set_id=option_set.id)  # Redirect to option list
    else:
        form = OptionForm(instance=option)

    return render(request, 'scale/edit_option.html', {'form': form, 'option': option, 'option_set': option_set})
