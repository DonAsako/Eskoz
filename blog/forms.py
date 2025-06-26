from django.forms import ModelForm
from .models import ArticleTranslation
from root.widgets import ContentEditorWidget


class ArticleTranslationAdminForm(ModelForm):
    class Meta:
        model = ArticleTranslation
        fields = "__all__"
        widgets = {"content": ContentEditorWidget}
