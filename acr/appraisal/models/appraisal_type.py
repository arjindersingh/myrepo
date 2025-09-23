
from django.db import models
from accounts.models.academicyear import AcademicYear
#from accounts.models.institute import Institute
from accounts.models.employee import JobCategory
from accounts.models.institute import Department, Institute, Subject, Wing
from appraisal.models.scale import Scale  # ✅ Importing JobCategory correctly

class AppraisalCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Name", help_text="Internal name of the appraisal category")
    short_name = models.CharField(max_length=20, unique=True, verbose_name="Short Name", help_text="Abbreviated form (e.g., code or acronym)")
    display_name = models.CharField(max_length=100, verbose_name="Display Name", help_text="User-friendly name shown in UI")
    description = models.TextField(blank=True, null=True, verbose_name="Description", help_text="Optional details about this appraisal category")

    class Meta:
        verbose_name = "Appraisal Category"
        verbose_name_plural = "Appraisal Categories"
        ordering = ["name"]

    def __str__(self):
        return self.display_name or self.name


class AppraisalType(models.Model):
    name = models.CharField(max_length=50, verbose_name="Appraisal Type Name", default="Appraisal Type Name")
    display_name = models.CharField(max_length=50,  verbose_name="Display Name", default="Appraisal Display Name")
    short_name = models.CharField(max_length=5,  verbose_name="Short Name of Appraisal Type", default="AT")
    at_category = models.ForeignKey(AppraisalCategory, on_delete=models.CASCADE, related_name="appraisals",  verbose_name="Appraisal Category", null=True, blank=True)

    at_job_categories = models.ManyToManyField(JobCategory, related_name="appraisal_types", verbose_name="Job Categories")
    at_institutes     = models.ManyToManyField(Institute, blank=True, related_name="appraisal_institutes", verbose_name="Institutes")
    at_departments    = models.ManyToManyField(Department, blank=True, related_name="appraisal_departments", verbose_name="Departments")
    at_wings          = models.ManyToManyField(Wing, blank=True, related_name="appraisal_wings", verbose_name="Wings")
    at_subjects       = models.ManyToManyField(Subject, blank=True, related_name="appraisal_subjects", verbose_name="Appraisal Subjects")
    
    # Appraisal Domain
    domain_name = models.CharField(max_length=50, verbose_name="Domain Name", default="Appraisal Domain Name")
    domain_description = models.CharField(max_length=100, verbose_name="Appraisal Domain Description", default="Appraisal Type Description"    )
    domain_weight = models.FloatField(default=100.0, verbose_name="Domain Weight (%)", help_text="Percentage weight indicating importance of this domain")

    # Appraisal Scale Information
    scale = models.ForeignKey(Scale, on_delete=models.CASCADE, related_name="appraisal_scale", verbose_name="Appraisal Scale", null = True)

    def __str__(self):
        return self.display_name or self.name 

    @classmethod
    def get_appraisal_type(cls,  pk):
        """ Return an AppraisalType instance by its primary key.
        Raises ObjectDoesNotExist if not found."""
        return cls.objects.get(pk=pk)
    
    
class AppraisalSchedule(models.Model):
    academic_year = models.ForeignKey(
        AcademicYear,  
        on_delete=models.CASCADE,  
        related_name="appraisal_schedules"  # updated related_name to be more accurate
    )
    appraisal_type = models.ForeignKey(
        AppraisalType, 
        on_delete=models.CASCADE, 
        related_name="schedules"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.CharField(
        max_length=100, 
        verbose_name="Appraisal Schedule  Description", 
        default="Appraisal Schedule Description"
    )
    created_date = models.DateTimeField(auto_now_add=True,  null=True,  blank=True)


    def __str__(self):
        return f"{self.academic_year} - {self.appraisal_type} ({self.start_date} to {self.end_date})"
    @classmethod
    def get_current_appraisal_schedule(cls,  appraisal_type):
        """         Returns the AppraisalSchedule for the current active AcademicYear (CAY)
        and the given appraisal_type.         """
        CAY = AcademicYear.get_active_academic_year()
        if isinstance(CAY,  int):
            CAY = AcademicYear.objects.filter(id=CAY).first()
        if not CAY:
            return None
        return cls.objects.filter(
            academic_year=CAY, 
            appraisal_type=appraisal_type
        ).first()
    @classmethod
    def check_appraisal_schedule_dates(cls,  appraisal_type):
        """Returns the AppraisalSchedule instance that matches the
        current academic year (CAY) and given appraisal_type (CAT).
        Returns None if no record exists."""
        # Get current academic year
        cay = AcademicYear.get_active_academic_year()
        if not cay:
            return None
        # Allow appraisal_type to be instance or id
        if isinstance(appraisal_type,  int):
            filter_kwargs = {"appraisal_type_id": appraisal_type}
        else:
            filter_kwargs = {"appraisal_type": appraisal_type}

        return cls.objects.filter(
            academic_year=cay, 
            **filter_kwargs
        ).first()
    

class EmpSelectionCriteria(models.Model):
    name = models.CharField(max_length=100, verbose_name="Name")
    display_name = models.CharField(max_length=100, verbose_name="Display Name")
    short_name = models.CharField(max_length=50, verbose_name="Short Name")
    default_value = models.BooleanField(default=False, verbose_name="Default Value")
    description = models.CharField(
        max_length=100,
        verbose_name="Appraisal Schedule Description",
        default="Appraisal Schedule Description"
    )

    def __str__(self):
        return self.display_name or self.name
    
class EmpSelectionData(models.Model):
    appraisal_type = models.ForeignKey(AppraisalType, on_delete=models.CASCADE, related_name="emp_selection_data"     )
    emp_selection_criteria = models.ForeignKey(EmpSelectionCriteria, on_delete=models.CASCADE, related_name="emp_selection_data" )
    value = models.BooleanField(default=False, verbose_name="Criteria Value")
    description = models.CharField(max_length=100, verbose_name="Employee Selection Description",default="Employee Selection Description"
    )
    created_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f" {self.appraisal_type} | {self.emp_selection_criteria}"
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[ 'appraisal_type', 'emp_selection_criteria'],
                name='uniq_emp_sel_per_type_crit'
            )
        ]
        indexes = [
            models.Index(fields=[ 'appraisal_type']),
            models.Index(fields=['emp_selection_criteria']),
        ]
    @classmethod
    def get_all_AT_settings(cls, CAT):
        """
        Return {short_name: bool} for all criteria for the given (CAT, CAY).
        Uses defaults from EmpSelectionCriteria when no saved value exists.
        """
        #from appraisal.models.appraisal_type import EmpSelectionCriteria  # avoid circular import if split models
        criteria = list(
            EmpSelectionCriteria.objects
            .only("id", "short_name", "default_value", "display_name")
        )
        saved = dict(
            cls.objects
            .filter(appraisal_type=CAT)
            .values_list("emp_selection_criteria_id", "value")
        )
        return {c.short_name: saved.get(c.id, c.default_value) for c in criteria}

    # ---------- READ ONE BY short_name ----------
    @classmethod
    def get_single_AT_setting(cls, CAT,  short_name: str, default: bool = False) -> bool:
        """
        Return the effective boolean for one setting identified by `short_name`.
        Falls back to the criterion's default_value; if the criterion doesn't exist, uses `default`.
        """
        #from appraisal.models.appraisal_type import EmpSelectionCriteria
        try:
            crit = EmpSelectionCriteria.objects.only("id", "default_value").get(short_name=short_name)
        except EmpSelectionCriteria.DoesNotExist:
            return default
        val = (cls.objects
               .filter(appraisal_type=CAT, emp_selection_criteria=crit)
               .values_list("value", flat=True)
               .first())
        return crit.default_value if val is None else bool(val)

    # ---------- (Optional) WRITE/UPSERT ----------
    @classmethod
    def set_single_AT_setting(cls, CAT, short_name: str, value: bool, description: str = "Employee Selection Description"):
        """
        Upsert a setting for (CAT, short_name). Handy if you want to change it in code.
        """
        #from appraisal.models.appraisal_type import EmpSelectionCriteria
        crit = EmpSelectionCriteria.objects.get(short_name=short_name)
        obj, _ = cls.objects.update_or_create(
            appraisal_type=CAT,
            emp_selection_criteria=crit,
            defaults={"value": value, "description": description},
        )
        return obj

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[ "appraisal_type", "emp_selection_criteria"],
                name="uniq_emp_sel_per_year_type_crit",
            )
        ]