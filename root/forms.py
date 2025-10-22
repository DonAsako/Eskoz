from django.forms import ModelForm
from django.contrib.auth.models import User
from root.widgets import ContentEditorWidget, OTPWidget
from root.models import Page, UserProfile


class PageAdminForm(ModelForm):
    class Meta:
        model = Page
        fields = "__all__"
        widgets = {"content": ContentEditorWidget}
