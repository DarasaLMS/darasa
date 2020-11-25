from django import forms
from .models import School
from .widgets import ColorInput


class SchoolAdminForm(forms.ModelForm):
    class Meta:
        exclude = []
        model = School
        widgets = {"primary_color": ColorInput, "secondary_color": ColorInput}
