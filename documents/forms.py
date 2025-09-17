from django import forms
from .models import UploadedDocument

class DocumentForm(forms.ModelForm):
    class Meta:
        model = UploadedDocument
        fields = ["file"]
