from django.db import models

class Subject(models.Model):
    subject_name = models.CharField(max_length=100, verbose_name="Subject Name")
    short_name = models.CharField(max_length=20, verbose_name="Short Name")
    description = models.TextField(blank=True, verbose_name="Description")

    def __str__(self):
        return self.subject_name

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"


class Course(models.Model):
    course_name = models.CharField(max_length=100, verbose_name="Course Name")
    short_name = models.CharField(max_length=20, verbose_name="Short Name")
    display_name = models.CharField(max_length=100, verbose_name="Display Name")
    subjects = models.ManyToManyField(Subject, verbose_name="Subjects")

    def get_subjects_for_semester(self, semester):
        """Returns subjects associated with a specific semester."""
        return self.subjects.filter(in_semester_year=semester)

    def get_courses_in_department(self, department):
        """Returns courses available in a specific department."""
        return Course.objects.filter(departmentname=department)

    def get_subjects(self):
        """Returns all subjects associated with the course."""
        return self.subjects.all()

    def __str__(self):
        return self.course_name

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"


class Department(models.Model):
    department_name = models.CharField(max_length=100, verbose_name="Department Name")
    short_name = models.CharField(max_length=20, verbose_name="Short Name")
    courses = models.ManyToManyField(Course, verbose_name="Courses")

    @classmethod
    def get_default_department(cls):
        """Returns the default department, usually 'Education'."""
        return cls.objects.filter(department_name="Education").first()

    def get_courses(self):
        """Returns all courses associated with this department."""
        return self.courses.all()
    @classmethod
    def get_default_department(cls):
        return cls.objects.first().id if cls.objects.exists() else None


    def __str__(self):
        return self.department_name

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"



class Wing(models.Model):
    """Represents a wing in the Institute (e.g., Science Wing, Arts Wing)."""
    name = models.CharField(max_length=50, verbose_name="Wing Name")
    description = models.TextField(blank=True, verbose_name="Description")

    def __str__(self):
        return self.name
    @classmethod
    def get_default_wing(cls):
        return cls.objects.first().id if cls.objects.exists() else None


    class Meta:
        verbose_name = "Wing"
        verbose_name_plural = "Wings"


class Institute(models.Model):
    institute_name = models.CharField(max_length=100, verbose_name="Institute Name")
    short_name = models.CharField(max_length=10, verbose_name="Short Name")
    address = models.TextField(verbose_name="Address")
    pincode = models.CharField(max_length=10, verbose_name="Pincode")
    phone = models.CharField(max_length=20, verbose_name="Phone")
    email = models.EmailField(verbose_name="Email")
    departments = models.ManyToManyField(Department, verbose_name="Departments")
    wings = models.ManyToManyField(Wing, verbose_name="Wings", blank=True)  # Added Wings field

    def __str__(self):
        return self.short_name

    @classmethod
    def get_all_institutes(cls):
        """Returns all registered institutes."""
        return cls.objects.all()
    @classmethod
    def get_default_institute(cls):
        return cls.objects.first().id if cls.objects.exists() else None

    class Meta:
        verbose_name = "Institute"
        verbose_name_plural = "Institutes"
