from django.forms import ModelForm
from .models import Article
from root.widgets import ContentEditorWidget


class ArticleAdminForm(ModelForm):
    class Meta:
        model = Article
        fields = "__all__"
        widgets = {"content": ContentEditorWidget}
