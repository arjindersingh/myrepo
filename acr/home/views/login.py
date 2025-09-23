from django.shortcuts import render
from appraisal.models.appraisal_type import AppraisalType
from django.utils import timezone

def ShowHomePage(request):

    context = {
        #"active_scheme": active_scheme,
    }
    return render(request, "home.html", context)
