from django import forms
from .models import Event
from .widgets import ColorInput


class EventAdminForm(forms.ModelForm):
    class Meta:
        exclude = []
        model = Event
        widgets = {"color": ColorInput}
