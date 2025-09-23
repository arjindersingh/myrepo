
from django.shortcuts import render


def show_appraisal_dashboard(request):
    return render(request, "appraisal_db.html")