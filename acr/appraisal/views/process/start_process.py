from django.shortcuts import redirect, render, get_object_or_404
from appraisal.models.app_excluded_emp import AppExcludedEmp
from accounts.models.employee import Employee
from appraisal.models.appraisal_data import TotalAppraisalData
from appraisal.models.appraisal_type import AppraisalType, AppraisalSchedule, EmpSelectionData
from accounts.context_processors import current_academic_year
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.decorators import menu_permission_required
from django.db.models import OuterRef, Subquery
from django.utils.safestring import mark_safe

@login_required
#@menu_permission_required
def start_appraisal_process(request, appraisal_type_id):
    # Fetch appraisal type  (404 if not found)
    try:
        CAT = AppraisalType.objects.get(pk=appraisal_type_id)
    except AppraisalType.DoesNotExist:
        messages.error(request, f"Appraisal Type with ID {appraisal_type_id} was not found.")
        return redirect("show_appraisal_dashboard")  
    
    #check for CU is self-assessor, is ASSESSOR OR IS INPECTOR based on Appraisal Category or not
    match CAT.at_category.id:
        case 1:
            # Self Assessor
            X= 2
        case 2: # Check CU is assessor or not in Profile settings
            CUIA = request.user.profile.is_assessor
            if CUIA is False:
                messages.error(request, f"Currently you are not having previleges of an Assessor. Contact System Administrator..")
                return redirect("show_appraisal_dashboard")  
        case 3: # Check CU is INSPECTOR or not in Profile settings
            CUIA = request.user.profile.is_inspector
            if CUIA is False:
                messages.error(request, f"Currently you are not having previleges of an Inspector. Contact System Administrator..")
                return redirect("show_appraisal_dashboard")  
    
    # Fetch Curent academic year
    try:
        CAY = current_academic_year()
    except AppraisalType.DoesNotExist:
        messages.error(request, f"There is probelm in fetching Current Academic year. Contact System Administrator..")
        return redirect("show_appraisal_dashboard")  # change to your desired URL name
    
    
        
    # Check appraisal schedule eligibility
    CAS = AppraisalSchedule.check_appraisal_schedule_dates(CAT.id)
    if CAS is None:
        messages.error(request, f"The Schedule to fill {CAT.display_name} has not started or is over. You can be before time or Late. Check the Schedule..")
        return redirect("show_appraisal_dashboard")  
    
    # Prepare the list of employees/assessees
    list_of_assessees = get_assessees_for_appraisal(request, CAY, CAT)
    
    # Pass data to template
    context = {
        "CAT": CAT,
        "Assessees": list_of_assessees,
        "CAS": CAS,  # optional, if template needs schedule
        
    }
    
    return render(request, "process/list_assessees.html", context)

def get_assessees_for_appraisal(request, CAY, CAT):
    CAT_id = CAT.id
    AT_assessee_settings = EmpSelectionData.get_all_AT_settings(CAT)
    ######## Code for Excluding CU from Self Appraisal    ################################
    if  CAT.pk == 1:
        if AT_assessee_settings.get("EXCLUDE_SELF", True) :
            emp_code = getattr(request.user.profile, "emp_code", None) 
            if emp_code:
                employees = Employee.objects.filter(emp_code=emp_code)
                return (employees)
            else:
                messages.error(request,"<strong>Profile Error:</strong><br>EMP Code")
                return redirect("show_appraisal_dashboard")
        else:
            messages.error(request,"<strong>Appraisal type Employee setting  Error:</strong><br>Exclused Self")
            return redirect("show_appraisal_dashboard")
    else:
        ########################## code for AT except Self Appraisal#####################
        # Get All the Employees
        employees = Employee.objects.all()
        emp_code = getattr(request.user.profile, "emp_code", None) 
        exclude_self = Employee.objects.filter(emp_code=emp_code).values_list('id', flat=True)
        #get all employees except excluded
        employees = (employees.exclude(id__in=exclude_self).distinct())
    
    ########################################################
    #employees = Employee.objects.filter(institutes__in=user_institutes).distinct()
    excluded_employees = (AppExcludedEmp.objects.filter(academic_year=CAY, appraisal_type=CAT_id)
        .values_list('ex_employee_id', flat=True))
    #get all employees except excluded
    employees = (Employee.objects.exclude(id__in=excluded_employees).distinct())

    ############################################################   
    #Filter employees for CAT permitted Job categories
    CAT_categories = CAT.at_job_categories.all()            
    employees = employees.filter(job_categories__in=CAT_categories).distinct()

    ############################################################
    #Filter employees for CAT permitted Job categories
    CAT_institutes = CAT.at_institutes.all()
    employees = employees.filter(institutes__in=CAT_institutes).distinct()

    ######################################################################################
    ######################## CU and Employees Filters Begins #############################
    ######################################################################################
       
    #################Filter employees for CU permitted Job categories####################
    if AT_assessee_settings.get("MATCH_JOB_CATEGORIES", True):
        try:
            match CAT.at_category.id:
                case 2:
                    CU_categories = request.user.profile.app_categories.all()
                case 3:
                    CU_categories = request.user.profile.inspection_categories.all()
            employees = employees.filter(job_categories__in=CU_categories)
        except Employee.DoesNotExist:
            return []
        """ else:
        messages.error(request,
                mark_safe(
                    f"<strong>Appraisal Type Settings Error:</strong>Job Categories<br>"
                    f"Current Appraisal Type <em>{CAT}</em> does not have an updated setting for "
                    f"Matching Job Categories of Current Assessor from the assessee list.<br>"
                    "Please update the appraisal type settings or contact the System Administrator."
                ),
            ) """
        #return redirect("show_appraisal_dashboard")
        
    #################Filter employees for CU permitted Institutes####################
    if AT_assessee_settings.get("MATCH_INSTITUTES", True):
        try:
            match CAT.at_category.id:
                case 2:
                    CU_institutes = request.user.profile.app_institutes.all()
                case 3:
                    CU_institutes = request.user.profile.inspection_institutes.all()
            employees = employees.filter(institutes__in=CU_institutes)
        except Employee.DoesNotExist:
            return []
        """ else:
        messages.error(request,
                mark_safe(
                    f"<strong>Appraisal Type Settings Error:</strong>Institutes <br>"
                    f"Current Appraisal Type <em>{CAT}</em> does not have an updated setting for "
                    f"Matching Institutes of Current Assessor from the assessee list.<br>"
                    "Please update the appraisal type settings or contact the System Administrator."
                ),
            ) """
        #return redirect("show_appraisal_dashboard")
    
    #################Filter employees for CU permitted Wings####################
    if AT_assessee_settings.get("MATCH_WINGS", True):
        try:
            CU_wings = request.user.profile.app_wings.all()
            employees = employees.filter(wings__in=CU_wings)
        except Employee.DoesNotExist:
            return []
        """ else:
        messages.error(request,
                mark_safe(
                    f"<strong>Appraisal Type Settings Error:</strong>Wings <br>"
                    f"Current Appraisal Type <em>{CAT}</em> does not have an updated setting for "
                    f"Matching Wings of Current Assessor from the assessee list.<br>"
                    "Please update the appraisal type settings or contact the System Administrator."
                ),
            ) """
        #return redirect("show_appraisal_dashboard")
    
    #################Filter employees for CU permitted Departements####################
    if AT_assessee_settings.get("MATCH_DEPARTMENTS", True):
        try:
            CU_departments = request.user.profile.app_departments.all()
            employees = employees.filter(departments__in=CU_departments)
        except Employee.DoesNotExist:
            return []
        """ else:
        messages.error(request,
                mark_safe(
                    f"<strong>Appraisal Type Settings Error:</strong>Departments <br>"
                    f"Current Appraisal Type <em>{CAT}</em> does not have an updated setting for "
                    f"Matching Departments of Current Assessor from the assessee list.<br>"
                    "Please update the appraisal type settings or contact the System Administrator."
                ),
            ) """
        #return redirect("show_appraisal_dashboard")
    #################Filter employees for CU permitted Subjects####################
    if AT_assessee_settings.get("MATCH_SUBJECTS", True):
        try:
            CU_subjects = request.user.profile.app_subjects.all()
            employees = employees.filter(subjects__in=CU_subjects)
        except Employee.DoesNotExist:
            return []
        """ else:
        messages.error(request,
                mark_safe(
                    f"<strong>Appraisal Type Settings Error:</strong>Subjects <br>"
                    f"Current Appraisal Type <em>{CAT}</em> does not have an updated setting for "
                    f"Matching Subjects of Current Assessor from the assessee list.<br>"
                    "Please update the appraisal type settings or contact the System Administrator."
                ),
            ) """
        #return redirect("show_appraisal_dashboard")
    ###############################################################
    # Subquery: latest TotalAppraisalData per employee for (CAY, CAT_id)
    latest_tad = (
        TotalAppraisalData.objects
        .filter(
            appraisal_year=CAY,
            appraisal_type_id=CAT_id,
            employee=OuterRef('pk'),
        )
        .order_by('-appraisal_no')
    )

    # 5) Annotate employees with latest TAD fields (if any)
    employees = employees.annotate(
        tad_id      = Subquery(latest_tad.values('id')[:1]),
        tad_no      = Subquery(latest_tad.values('appraisal_no')[:1]),
        tad_created_on     = Subquery(latest_tad.values('created_on')[:1]),
        tad_obt     = Subquery(latest_tad.values('obt_score')[:1]),
        tad_remarks = Subquery(latest_tad.values('remarks')[:1]),
    )

    #  De-duplicate at the end (M2M joins can create dups)
    employees = employees.distinct()
    return list(employees)
       

