from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import Group
from django.contrib import messages
from accounts.decorators import menu_permission_required
from accounts.forms.user_group import GroupForm

# List all groups
@menu_permission_required
def group_list(request):
    groups = Group.objects.all()
    return render(request, 'user_groups/list.html', {'groups': groups})

# Create a new group
def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Group created successfully!')
            return redirect('user_group_list')
    else:
        form = GroupForm()
    return render(request, 'user_groups/create.html', {'form': form})

# Edit an existing group
def edit_group(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, 'Group updated successfully!')
            return redirect('user_group_list')
    else:
        form = GroupForm(instance=group)
    return render(request, 'user_groups/edit.html', {'form': form})

# Delete an existing group
def delete_group(request, pk):
    group = get_object_or_404(Group, pk=pk)
    group.delete()
    messages.success(request, 'Group deleted successfully!')
    return redirect('user_group_list')