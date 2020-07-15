from django import forms


class ImageUploaderWidget(forms.ClearableFileInput):
    template_name = "widgets/image_uploader.html"

    class Media:
        css = {"all": ("/static/css/avatar.css",)}
        js = ("/static/js/avatar.js",)
