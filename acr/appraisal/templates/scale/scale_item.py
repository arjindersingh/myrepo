from django.shortcuts import render, get_object_or_404, redirect
from appraisal.models.scale import Scale, Item
from appraisal.forms.item import ItemForm

def add_scale_items(request, scale_id):
    scale = get_object_or_404(Scale, id=scale_id)
    items = scale.items.all().select_related("option_set").prefetch_related("option_set__options")

    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.scale = scale
            item.save()
            return redirect("add_scale_Items", scale_id=scale.id)
    else:
        form = ItemForm()

    return render(request, "scale/add_scale_item.html", {
        "form": form,
        "scale": scale,
        "items": items,
    })


def edit_scale_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    scale = item.scale
    items = scale.items.all().select_related("option_set").prefetch_related("option_set__options")

    if request.method == "POST":
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("add_scale_Items", scale_id=scale.id)
    else:
        form = ItemForm(instance=item)

    return render(request, "scale/edit_scale_item.html", {
        "form": form,
        "item": item,
        "scale": scale,
        "items": items,   # 👈 pass items list
    })


def delete_scale_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    scale_id = item.scale.id
    item.delete()  # Only deletes the Item, not OptionSet or Options
    return redirect("add_scale_Items", scale_id=scale_id)