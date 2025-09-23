from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import resolve
from accounts.models.menu import UserGroupMenuPermission, UserMenuPermission
from accounts.models.userprofile import UserProfile

def menu_permission_required(view_func):
    """Decorator to check if logged-in user has menu permission via group or direct user access."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect("login")      
        # Get the current URL name
        current_url_name = resolve(request.path_info).url_name
        # --- Check group-based permissions ---
        try:
            user_profile = request.user.profile
            user_groups = user_profile.user_groups.all()
        except UserProfile.DoesNotExist:
            user_groups = []

        has_group_permission = any(
            UserGroupMenuPermission.objects.filter(
                group=group, menu__UrlName=current_url_name, can_access=True
            ).exists() for group in user_groups
        )

        # --- Check direct user-based permissions ---
        user_permission_entry = UserMenuPermission.objects.filter(
            user=request.user, menu__UrlName=current_url_name
        ).first()

        has_user_permission = bool(user_permission_entry and user_permission_entry.can_access)
        has_user_entry = bool(user_permission_entry)  # means user has explicit entry, even if False

        # --- Final decision logic ---
        if not has_group_permission :
            # No group permission and no individual record
            messages.error(request, "Your group does not allow you to use this menu.")
            return redirect(request.META.get("HTTP_REFERER", "ShowHomePage"))

        if  has_group_permission and not has_user_entry:
            # No group permission and no individual record
            messages.error(request, "Your group does not allow you to use this menu.")
            return redirect(request.META.get("HTTP_REFERER", "ShowHomePage"))

        if has_user_permission:
            return view_func(request, *args, **kwargs)

        if has_group_permission and has_user_entry and not has_user_permission:
            # User’s explicit denial overrides group allowance
            messages.error(request, "You are not allowed to use this menu individually despite having group permission.")
            return redirect(request.META.get("HTTP_REFERER", "ShowHomePage"))

        if not has_group_permission and has_user_entry and not has_user_permission:
            # No group permission + explicit user denial
            messages.error(request, "Neither your group nor you individually have permission to use this menu.")
            return redirect(request.META.get("HTTP_REFERER", "ShowHomePage"))

        
        return view_func(request, *args, **kwargs)
     
    return _wrapped_view


""" def menu_permission_required(view_func):
    ""Decorator to check if the logged-in user's groups (from UserProfile) have menu permission."""
    #@wraps(view_func)
"""def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect("login")  # Redirect to login if not authenticated
        
        # Get the current URL name
        current_url_name = resolve(request.path_info).url_name
        # Get the user's profile and associated groups
        try:
            user_profile = request.user.profile
            user_groups = user_profile.user_groups.all()  # Get groups from UserProfile
        except UserProfile.DoesNotExist:
            messages.error(request, "User profile not found.")
            return redirect("ShowHomePage")  # Redirect to home if no profile found

        # Check if any of the user's profile groups have permission for the menu
        has_permission = any(
            UserGroupMenuPermission.objects.filter(
                group=group, menu__UrlName=current_url_name, can_access=True
            ).exists() for group in user_groups
        )

        if not has_permission:
            messages.error(request, "You do not have permission to access this page.")
            return redirect(request.META.get("HTTP_REFERER", "ShowHomePage"))  # Redirect back

        return view_func(request, *args, **kwargs)
     
    return _wrapped_view """