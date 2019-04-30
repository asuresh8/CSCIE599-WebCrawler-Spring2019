from django.forms import ModelForm, HiddenInput
from .models import CrawlRequest, Profile, MlModel

class CrawlRequestForm(ModelForm):
    class Meta:
        model = CrawlRequest
        fields = ('name', 'type', 'domain', 'urls', 'description', 'docs_all', 'docs_html', 'docs_docx', 'docs_pdf', 'docs_xml', 'docs_txt', 'num_crawlers', 'model', 'model_labels')
        labels = {
            'name': 'Job Name',
            'type': 'Crawl Type',
            'domain': 'Domain',
            'urls': 'URLs to crawl',
            'description': 'Description',
            'docs_all': 'Collect everything',
            'docs_html': 'Collect HTML files',
            'docs_docx': 'Collect DOCX files',
            'docs_pdf': 'Collect PDF files',
            'docs_xml': 'Collect XML files',
            'docs_txt': 'Collect TXT files',
            'num_crawlers': 'Number of crawler instances',
            'model' : 'Model Name',
            'model_labels' : 'Model Classification Labels',
        }
        widgets = {
            'user': HiddenInput(),
            'created': HiddenInput(),
            'modified': HiddenInput(),
            'docs_collected': HiddenInput(),
            'status': HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        """ Instantiates an onject of type ProfileForm with custom widget attributes """
        super(CrawlRequestForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Crawl Job Name'})
        self.fields['type'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Crawl Type'})
        self.fields['domain'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Domain'})
        self.fields['urls'].widget.attrs.update({'class': 'form-control', 'placeholder': 'URLs to crawl'})
        self.fields['description'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Crawl Notes'})
        self.fields['docs_all'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Collect everything'})
        self.fields['docs_html'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Collect HTML files'})
        self.fields['docs_docx'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Collect DOCX files'})
        self.fields['docs_pdf'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Collect PDF files'})
        self.fields['docs_xml'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Collect XML files'})
        self.fields['docs_txt'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Collect TXT files'})
        self.fields['num_crawlers'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Number crawler instances'})
        self.fields['model'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Model Name'})
        self.fields['model_labels'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Model Classification Labels'})



class ProfileForm(ModelForm):
    """ Form to show a user's profile data """
    class Meta:
        """ The meta class to set several important parameters for the form """
        model = Profile
        fields = ['s3_bucket', 'api_key', 'api_secret', 'num_crawlers']
        labels = {
            's3_bucket': 'Enter AWS S3 URL',
            'api_key': 'S3 API Key',
            'api_secret': 'Secret',
            'num_crawlers': 'Number of crawlers',
        }
        widgets = {
            'user': HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        """ Instantiates an onject of type ProfileForm with custom widget attributes """
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['s3_bucket'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter AWS S3 URL'})
        self.fields['api_key'].widget.attrs.update({'class': 'form-control', 'placeholder': 'S3 API Key'})
        self.fields['api_secret'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Secret'})
        self.fields['num_crawlers'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Number of concurrent crawler instances'})

class MlModelForm(ModelForm):
    """ Form to show a ml_model's data """
    class Meta:
        """ The meta class to set several important parameters for the form """
        model = MlModel
        fields = ['name', 'labels']
        labels = {
            'name': 'Enter Model Name',
            'labels': 'Enter Model Labels',
        }
        widgets = {
            'user': HiddenInput(),
            'created': HiddenInput(),
            'modified': HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        """ Instantiates an onject of type ProfileForm with custom widget attributes """
        super(MlModelForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter Model'})
        self.fields['labels'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter Model Labels'})