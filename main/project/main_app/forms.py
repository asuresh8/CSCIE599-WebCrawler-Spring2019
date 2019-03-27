from django.forms import ModelForm, HiddenInput
from .models import CrawlRequest, Profile

class CrawlRequestForm(ModelForm):
    class Meta:
        model = CrawlRequest
        exclude = ('user', 'created', 'modified', 'docs_collected', 'status')


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
