from django.urls import path, reverse_lazy
from accounts.views.academi_year import AcademicYearCreateView, AcademicYearListView, SetActiveAcademicYearView
from accounts.views.account import show_account_dashboard
from accounts.views.emp_bulk_upload import employee_bulk_upload

from accounts.views.setting import setting_edit, setting_list, update_user_settings
#from accounts.views.user import list_users
from .views.authentication import login_user , logout_user, show_dashboard, register_user
from django.contrib.auth.views import LoginView
from django.contrib.auth import views as auth_views
from accounts.views.userprofile import edit_basic_user_profile, edit_pro_user_profile,  list_user_profiles
from accounts.views import user_groups as User_group_management_views
from .views.menu import manage_group_menu_permissions, manage_user_menu_permissions
from accounts.views.employee import list_employees, create_employee, view_employee_detail, edit_employee, delete_employee
from accounts.views import  authentication # for custom success email handler



urlpatterns = [
    path('login/', login_user, name='LoginUser'),
    path('logout/', logout_user, name='LogoutUser'),
    path('sdb/', show_dashboard, name='ShowDashboard'),
    path('sacdb/', show_account_dashboard, name='ShowAccountDashboard'),
    path('register/', register_user, name='RegisterUser'),
    #Password Change URLS
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            email_template_name='registration/password_reset_email.html',
            success_url=reverse_lazy('password_reset_done')  # ✅ More robust than hardcoding
        ),
        name='password_reset'
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path('reset/<uidb64>/<token>/', authentication.CustomPasswordResetConfirmView.as_view(), 
        name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html'
        ), 
        name='password_reset_complete'),
    #path("profile/password/", password_change_using_profile, name="password_change_using_profile"),
    # Academic Years
    path('', AcademicYearListView.as_view(), name='academic_year_list'),
    path('create/', AcademicYearCreateView.as_view(), name='academic_year_create'),
    path('set-active/', SetActiveAcademicYearView.as_view(), name='set_active_academic_year'),
    # user Management Groups and permissions
    # Menu management 
    path('mgmp/<int:group_id>/', manage_group_menu_permissions, name='manage_group_menu_permissions'),
    path('mump/<int:user_id>/', manage_user_menu_permissions, name='manage_user_menu_permissions'),
    # User 
    #path("users/", list_users, name="list_users"),  # ✅ URL for listing users
    path('usergrouplist', User_group_management_views.group_list, name='user_group_list'),
    path('createusergroup/', User_group_management_views.create_group, name='create_user_group'),
    path('editusergroup/<int:pk>/', User_group_management_views.edit_group, name='edit_user_group'),
    path('deleteusergroup/<int:pk>/', User_group_management_views.delete_group, name='delete_group'),  # Add delete URL
    # user profile related urls
    path("ebup/", edit_basic_user_profile, name="edit_basic_user_profile"),  # ✅ User edits their own profile
    path("epup/<int:user_id>/", edit_pro_user_profile, name="edit_pro_user_profile"),  # ✅ Admin edits any user's profile
    #path("efup/<int:user_id>/", edit_full_user_profile, name="edit_full_user_profile"),
    path("profiles/", list_user_profiles, name="list_user_profiles"),  # ✅ URL for user profiles
    #Employee
    path('le', list_employees, name='list_employees'),
    path('ce/', create_employee, name='create_employee'),
    path('ve/<int:emp_id>/', view_employee_detail, name='view_employee_detail'),
    path('ee/<int:emp_id>/edit/', edit_employee, name='edit_employee'),
    path('de/<int:emp_id>/delete/', delete_employee, name='delete_employee'),
    path("ebu/", employee_bulk_upload, name="employee_bulk_upload"),
    
    # Settings 
    path('settings/', setting_list, name='setting_list'),
    path('settings/edit/<int:setting_id>/', setting_edit, name='setting_edit'),
    path('uus/<int:user_id>/', update_user_settings, name='update_user_settings'),
    
    
]
