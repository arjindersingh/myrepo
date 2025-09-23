from django import forms

class EmpSelectionSettingsForm(forms.Form):
    """
    Dynamically built form: one Boolean field per EmpSelectionCriteria.
    Field name key: f"crit_{pk}"
    Label: display_name; Help text: description
    """
    def __init__(self, *args, criteria_qs=None, initial_values=None, **kwargs):
        super().__init__(*args, **kwargs)
        criteria_qs = criteria_qs or []
        initial_values = initial_values or {}
        for crit in criteria_qs:
            field_name = f"crit_{crit.pk}"
            self.fields[field_name] = forms.BooleanField(
                required=False,
                label=crit.display_name or crit.name,
                help_text=crit.description,
                initial=initial_values.get(crit.pk, crit.default_value),
            )
