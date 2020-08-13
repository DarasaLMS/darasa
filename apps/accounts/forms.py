from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import ugettext_lazy as _
from .models import User, School
from .widgets import ImageUploaderWidget, ColorInput


class UserAddForm(forms.ModelForm):
    """A form for creating a new user account.

    Includes all the required fields, plus a repeated password.
    """

    picture = forms.ImageField(
        label="Picture", widget=ImageUploaderWidget, required=False
    )
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ()

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserAddForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users.

    Includes all the fields on the user,
    but replaces the password field with admin's password hash display field.
    """

    picture = forms.ImageField(
        label="Picture", required=False, widget=ImageUploaderWidget
    )
    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_(
            "Raw passwords are not stored, so there is no way to see "
            "this user's password, but you can change the password "
            'using <a href="password/">this form</a>.'
        ),
    )

    class Meta:
        model = User
        fields = "__all__"

    def clean_password(self):
        return self.initial["password"]


class SchoolAdminForm(forms.ModelForm):
    class Meta:
        exclude = []
        model = School
        widgets = {"color": ColorInput}

