from django import forms
from django.forms import modelformset_factory, inlineformset_factory
from appraisal.models.scale import Scale,  Item, OptionSet, Option

# Form for Scale

class ScaleForm(forms.ModelForm):
    class Meta:
        model = Scale
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Scale Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Scale Description', 'rows': 3}),
        }

""" 
# Form for Dimension
class DimensionForm(forms.ModelForm):
    class Meta:
        model = Dimension
        fields = ['name', 'description', 'scale']

# Form for OptionSet
class OptionSetForm(forms.ModelForm):
    class Meta:
        model = OptionSet
        fields = ['name']

# Form for Option
class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['text', 'value', 'option_set']

# Form for Item
class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['scale', 'dimension', 'statement', 'option_set']  # Include necessary fields

# Formset for Items
ItemFormSet = inlineformset_factory(
    Dimension,  # Parent model (Dimension has a ForeignKey to Item)
    Item,       # Child model (Item contains a ForeignKey to OptionSet)
    form=ItemForm,
    extra=1      # Adjust as needed
)

# Formsets for each model (to allow adding multiple related objects)
DimensionFormSet = inlineformset_factory(Scale, Dimension, form=DimensionForm, extra=1)
ItemFormSet = inlineformset_factory(Dimension, Item, form=ItemForm, extra=1)

OptionFormSet = inlineformset_factory(OptionSet, Option, form=OptionForm, extra=1)
OptionSetFormSet = forms.modelformset_factory(OptionSet, form=OptionSetForm, extra=1) """