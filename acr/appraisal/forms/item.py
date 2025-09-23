from django import forms
from appraisal.models.scale import Item, Scale, OptionSet

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["statement", "option_set"]  # Fields to be filled by the user
        widgets = {
            "statement": forms.Textarea(attrs={"class": "form-control", "placeholder": "Enter Item Question", "rows": 4}),
            "option_set": forms.Select(attrs={"class": "form-select"}),
        }



class ItemEditForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['scale',  'statement', 'option_set']

    scale = forms.ModelChoiceField(
        queryset=Scale.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    statement = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
    )
    option_set = forms.ModelChoiceField(
        queryset=OptionSet.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )