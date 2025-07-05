from django.forms import ModelForm
from .models import Page, Theme
from root.widgets import ContentEditorWidget


class PageAdminForm(ModelForm):
    class Meta:
        model = Page
        fields = "__all__"
        widgets = {"content": ContentEditorWidget}
