from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from accounts.models.menu import Menu, UserGroupMenuPermission, UserMenuPermission
from django.shortcuts import redirect, render, get_object_or_404
from accounts.models.menu import Menu, UserGroupMenuPermission
from accounts.models.userprofile import UserProfile
from accounts.views.authentication import User

def get_user_allowed_menus(user):
    """Returns menus that a user has permission to access based on their group."""
    
    if user.is_superuser:
        return Menu.objects.filter(is_active=True).order_by("Command_Depth", "Command_Sequence")

    user_groups = user.groups.all()
    
    allowed_menus = Menu.objects.filter(
        id__in=UserGroupMenuPermission.objects.filter(
            group__in=user_groups, can_access=True
        ).values_list("menu", flat=True),
        is_active=True
    ).order_by("Command_Depth", "Command_Sequence")

    return allowed_menus

""" @login_required
def display_users_to_manage_permissions(request):
    user = request.user  # Logged-in user

    # Get all menus allowed to be shown
    menus = Menu.get_menus_with_display_permission()

    # Create a dictionary {menu_id: can_access}
    permissions = {
        perm.menu.id: perm.can_access
        for perm in UserMenuPermission.objects.filter(user=user)
    }

    if request.method == 'POST':
        for menu in menus:
            can_access = request.POST.get(f'can_access_{menu.id}') == 'on'
            perm, created = UserMenuPermission.objects.get_or_create(
                user=user, 
                menu=menu
            )
            perm.can_access = can_access
            perm.save()
        return redirect('users_list')  # Replace with your real URL name

    return render(request, 'menu/modify_user_permissions.html', {
        'user': user,
        'menus': menus,
        'permissions': permissions
    }) """

@login_required
def manage_group_menu_permissions(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    menus = Menu.get_menus_with_display_permission()    #menus = Menu.objects.all() 
    permissions = {perm.menu.id: perm.can_access for perm in UserGroupMenuPermission.objects.filter(group=group)}
    
    if request.method == 'POST':
        group_id = request.POST.get('group_id')  # Or from URL kwargs
        group = get_object_or_404(Group, pk=group_id)

        for menu in menus:
            can_access = request.POST.get(f'can_access_{menu.id}', 'off') == 'on'
            perm, created = UserGroupMenuPermission.objects.get_or_create(
                group=group,
                menu=menu
            )
            perm.can_access = can_access
            perm.save()

        return redirect('user_group_list')
    
    return render(request, 'menu/modify_group_permissions.html', {
        'group': group,
        'menus': menus,
        'permissions': permissions
    })

@login_required
def manage_user_menu_permissions(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user_profile = UserProfile.objects.get(user_id=user)
    menus = Menu.get_menus_with_display_permission()    #menus = Menu.objects.all() 
    permissions = {perm.menu.id: perm.can_access for perm in UserMenuPermission.objects.filter(user=user)}
    
    if request.method == 'POST':
        for menu in menus:
            can_access = request.POST.get(f'can_access_{menu.id}', 'off') == 'on'
            perm, created = UserMenuPermission.objects.get_or_create(
                user=user,
                menu=menu
            )
            perm.can_access = can_access
            perm.save()

        return redirect('list_user_profiles')
    
    return render(request, 'menu/modify_user_menu_permissions.html', {
        'user': user,
        'user_profile': user_profile,
        'menus': menus,
        'permissions': permissions
    })