from django.forms import ModelForm
from .models import Page, Theme
from root.widgets import ContentEditorWidget, ColorPickerWidget


class PageAdminForm(ModelForm):
    class Meta:
        model = Page
        fields = "__all__"
        widgets = {"content": ContentEditorWidget}


class ThemeAdminForm(ModelForm):
    class Meta:
        model = Theme
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            if field_name.endswith("_color"):
                self.fields[field_name].widget = ColorPickerWidget()
