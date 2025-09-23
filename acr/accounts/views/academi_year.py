from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.forms.models import model_to_dict

from accounts.models.academicyear import AcademicYear
from accounts.forms.academic_year import AcademicYearForm

class AcademicYearListView(View):
    def get(self, request):
        years = AcademicYear.objects.all()
        add_form = AcademicYearForm()
        return render(request, "academic_year/list.html", {
            "years": years,
            "add_form": add_form
        })

@method_decorator(csrf_exempt, name='dispatch')
class AcademicYearCreateView(View):
    def post(self, request):
        form = AcademicYearForm(request.POST)
        if form.is_valid():
            year = form.save()
            return JsonResponse({
                "status": "success",
                "year": model_to_dict(year)
            })
        return JsonResponse({"status": "error", "errors": form.errors}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class SetActiveAcademicYearView(View):
    def post(self, request):
        year_id = request.POST.get("year_id")
        year = get_object_or_404(AcademicYear, id=year_id)
        year.is_active = True
        year.save()
        return JsonResponse({"status": "success", "active_id": year.id})
