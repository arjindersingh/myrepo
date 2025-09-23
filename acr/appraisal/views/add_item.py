from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from appraisal.models.scale import Scale, Item, OptionSet
from appraisal.forms.item import ItemForm
from django.http import JsonResponse
from appraisal.forms.item import ItemEditForm
def add_item(request, scale_id, dimension_id):
    # Fetch the scale and dimension using the provided ids
    scale = get_object_or_404(Scale, id=scale_id)
    
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.scale = scale  # Link the item to the scale
            item.save()
            return redirect(reverse("show_scale_list"))  # Redirect to the list of scales after saving the item
    else:
        form = ItemForm()

    return render(request, "scale/add_item.html", {"form": form, "scale": scale})



def edit_all_items(request):
    selected_scale_id = request.GET.get("scale")
    scales = Scale.objects.all()

    if selected_scale_id:
        items = Item.objects.filter(scale_id=selected_scale_id)
    else:
        items = Item.objects.all()

    if request.method == "POST":
        for item in items:
            form = ItemEditForm(request.POST, instance=item, prefix=str(item.id))
            if form.is_valid():
                form.save()

    # Recreate forms after POST or for initial render
    forms = [ItemEditForm(instance=item, prefix=str(item.id)) for item in items]

    context = {
        "items": zip(items, forms),
        "scales": scales,
        "selected_scale_id": selected_scale_id,
    }
    return render(request, "scale/edit_all_items.html", context)