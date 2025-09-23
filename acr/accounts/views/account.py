
from django.shortcuts import render


def show_account_dashboard(request):
    return render(request, "account_db.html")