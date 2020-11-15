from django import forms


class ActivitySearchForm(forms.Form):
    start_date = forms.DateField()
    end_date = forms.DateField()
