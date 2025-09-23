from accounts.models.employee import Employee
from accounts.models.userprofile import UserProfile
from accounts.models.menu import Menu, UserGroupMenuPermission
from accounts.views.menu import get_user_allowed_menus
from accounts.models.academicyear import AcademicYear

def user_context(request):
    """Adds logged-in user's  information to all templates."""
    if request.user.is_authenticated:
        try:
            profile = request.user.profile  # Get user profile
            return {
                "CU_emp_code": profile.emp_code,
                "display_name": profile.display_name,
                "institute": profile.user_institutes, # Employee.get_employee_detail_by_code(profile.emp_code),  # Add institute info to templates
                #"department": profile.department,
                #"subject": profile.subject,
                "user_profile": profile,  # User profile (for other details if needed)
            }
        except UserProfile.DoesNotExist:
            return {}  # Return empty context if profile doesn't exist
    return {}  # Return empty context for unauthenticated users


def current_academic_year(request=None):
    """
    Returns the current AcademicYear.
    - If called without request -> returns the AcademicYear instance (for views).
    - If called with request   -> returns {'CAY': instance} (for context processor).
    """
    cay = AcademicYear.get_active_academic_year()
    if isinstance(cay, int):
        cay = AcademicYear.objects.filter(id=cay).first()

    # If Django calls it as context processor, wrap in dict
    if request is not None:
        return {"CAY": cay}

    # If called manually from views, just return the instance
    return cay
