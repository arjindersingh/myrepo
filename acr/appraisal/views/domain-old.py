""" from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from accounts.decorators import menu_permission_required
#from appraisal.models.domain import Domain
from accounts.models.setting import UserSetting
from appraisal.forms.domain import DomainForm

@menu_permission_required
def acr_domain_list(request):
    search_query = request.GET.get('search', '')
    per_page = UserSetting.get_user_setting(request, "pagination_limit") or 10  # Default to 10 if setting is missing
    #print (per_page)
    #acr_domains = Domain.objects.all().order_by("-id")
    if search_query:
        acr_domains = acr_domains.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        ).order_by("id")  # Keep ordering after filtering

    paginator = Paginator(acr_domains, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'acr_domain/list.html', {'page_obj': page_obj, 'search_query': search_query})

def acr_domain_create(request):
    if request.method == 'POST':
        form = DomainForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "ACR Domain created successfully!")
            return redirect('list_acr_domain')
    else:
        form = DomainForm()
    return render(request, 'acr_domain/add_edit.html', {'form': form})

def acr_domain_update(request, pk):
    #acr_domain = get_object_or_404(Domain, pk=pk)
    if request.method == 'POST':
        form = DomainForm(request.POST, instance=acr_domain)
        if form.is_valid():
            form.save()
            messages.success(request, "ACR Domain updated successfully!")
            return redirect('list_acr_domain')
    else:
        form = DomainForm(instance=acr_domain)
    return render(request, 'acr_domain/add_edit.html', {'form': form})

def acr_domain_delete(request, pk):
    #acr_domain = get_object_or_404(Domain, pk=pk)
    if request.method == 'POST':
        acr_domain.delete()
        messages.success(request, "ACR Domain deleted successfully!")
        return redirect('acr_domain_list')
    return render(request, 'acr_domain/delete.html', {'acr_domain': acr_domain})
 """