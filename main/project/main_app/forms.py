from django.forms import ModelForm

from .models import CrawlRequest

class CrawlRequestForm(ModelForm):
    class Meta:
        model = CrawlRequest
        exclude = ('user', 'created', 'modified', 'docs_collected', 'status')
