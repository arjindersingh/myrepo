from django.urls import path
from appraisal.templates.scale.scale_item import add_scale_items, delete_scale_item, edit_scale_item
from appraisal.views.add_item import edit_all_items
from appraisal.views.appraisal import show_appraisal_dashboard
from appraisal.views.emp_selection_setting import emp_selection_settings_for_appraisal_type
from appraisal.views.process.start_process import start_appraisal_process
from appraisal.views.process.fill_appraisal import show_appraisal_form
from appraisal.views.reports.consolidated import show_appraisal_consolidated_Report 
from appraisal.views.reports.total_appraisals import list_total_appraisals, delete_total_appraisal
from appraisal.views.scale import edit_scale, scale_list, add_scale
from appraisal.views.option_set import add_option_set, list_option_set
from appraisal.views.option import add_option, edit_option
#from appraisal.views.domain import acr_domain_create, acr_domain_update, acr_domain_list, acr_domain_delete
from appraisal.views.appraisal_type import  appraisal_type_create, appraisal_type_delete,appraisal_type_detail,appraisal_type_edit,appraisal_type_list
from appraisal.views.appraisal_schedule import appraisal_schedule_add, appraisal_schedule_delete,  appraisal_schedule_edit, appraisal_schedule_list
from appraisal.views.app_excluded_emp import   manage_app_excluded_emps, app_ex_employee_lookup, delete_app_excluded_emp
urlpatterns = [
    path("sapdb", show_appraisal_dashboard, name="show_appraisal_dashboard"),
    # Domains
    #path("lad/", acr_domain_list, name="list_acr_domain"),
    #path("aad/", acr_domain_create, name="add_acr_domain"),
    #path("ead/<int:pk>/", acr_domain_update, name="edit_acr_domain"),
    #path("dad/<int:pk>/", acr_domain_delete, name="delete_acr_domain"),
    #Scale 
    path('scales/', scale_list, name='show_scale_list'),
    path('add_scale/', add_scale, name='add_scale'),
    path('es/<int:pk>/', edit_scale, name='edit_scale'),
    path('eai/', edit_all_items, name='edit_all_items'),
    path("asi<int:scale_id>/", add_scale_items, name="add_scale_Items"),
    path("esi/<int:item_id>/", edit_scale_item, name="edit_scale_item"),
    path("dsi/<int:item_id>/", delete_scale_item, name="delete_scale_item"),
    # Option Set and Options
    path('los/', list_option_set, name='list_option_set'),  # List view
    path('os/add/', add_option_set, name='add_option_set'),  # Add view
    path('ao/<int:option_set_id>/', add_option, name='add_option'),  # Add option
    path('eo/<int:option_id>/', edit_option, name='edit_option'),
    # Appraisal Type
    path('apl/', appraisal_type_list, name='appraisal_type_list'),
    path('aat/', appraisal_type_create, name='appraisal_type_create'),
    path('eat/<int:pk>/', appraisal_type_edit, name='appraisal_type_edit'),
    path('dat/<int:pk>/', appraisal_type_detail, name='appraisal_type_detail'),
    path('delat/<int:atype_id>/', appraisal_type_delete, name='appraisal_type_delete'),
    #Appraisla Schedule
    path('as/<int:appraisal_type_id>/', appraisal_schedule_list, name='appraisal_schedule_list'),
    path('aas/<int:appraisal_type_id>', appraisal_schedule_add, name='appraisal_schedule_add'),
    path('eas/<int:schedule_id>/',  appraisal_schedule_edit, name='appraisal_schedule_edit'),
    path('das/<int:schedule_id>/', appraisal_schedule_delete, name='appraisal_schedule_delete'),
    # Excluded employee from apprisal list for each user for CAY
    path("aee/", manage_app_excluded_emps, name="manage_app_ex_emp"),
    path("aeel/", app_ex_employee_lookup, name="employee-lookup"),
    path("daee/<int:pk>/delete/", delete_app_excluded_emp, name="excluded-delete"),
    # Appraisal Employee Selection for Appraisla Type
    path("esefat/<int:appraisal_type_id>/", emp_selection_settings_for_appraisal_type, name="emp_selection_settings_for_appraisal_type",),
    # Appraisal Process
    path('sap/<int:appraisal_type_id>/', start_appraisal_process, name='start_appraisal_process'),
    path("fill_appraisal/<int:appraisal_type_id>/<int:employee_id>/", show_appraisal_form, name="show_appraisal_form"),
    #Appraisal Reports 
    path("sacr/", show_appraisal_consolidated_Report, name="show_appraisal_consolidated_Report"),
    path("total/", list_total_appraisals, name="total_appraisals"),
    path("total/delete/<int:pk>/", delete_total_appraisal, name="delete_total_appraisal"),

    
]
