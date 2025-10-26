from django.forms import ModelForm

from root.widgets import ContentEditorWidget

from .models import PostTranslation


class PostTranslationAdminForm(ModelForm):
    class Meta:
        model = PostTranslation
        fields = "__all__"
        widgets = {"content": ContentEditorWidget}
