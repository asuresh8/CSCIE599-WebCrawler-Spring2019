from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class CrawlRequest(models.Model):
    """
    The model to represent a crawl request.
    """
    CRAWLTYPES = (
        (1, 'All content from a single domain'),
        (2, 'Content from multiple URLs')
    )
    STATUS = (
        (1, 'Created'),
        (2, 'In progress'),
        (3, 'Finished'),
        (4, 'Failed')
    )
    name = models.CharField(max_length=128)
    type = models.PositiveSmallIntegerField("crawl type", default=1, choices=CRAWLTYPES)
    domain = models.URLField(default='', max_length=500, blank=True)
    urls = models.TextField(default='', max_length=1000, blank=True)
    description = models.TextField(default='', max_length=1000, blank=True)
    docs_all = models.BooleanField(default=False, blank=True)
    docs_html = models.BooleanField(default=False, blank=True)
    docs_docx = models.BooleanField(default=False, blank=True)
    docs_pdf = models.BooleanField(default=False, blank=True)
    docs_xml = models.BooleanField(default=False, blank=True)
    docs_txt = models.BooleanField(default=False, blank=True)
    docs_collected = models.PositiveIntegerField(default=0, blank=True)
    status = models.PositiveSmallIntegerField("crawl status", default=1, choices=STATUS)
    s3_location = models.URLField(default='', max_length=1000, blank=True)
    crawler_manager_endpoint = models.URLField(default='', max_length=500, blank=True)
    manifest = models.URLField(default='', max_length=1000, blank=True)
    num_crawlers = models.PositiveIntegerField("Number crawler instances", default=1)
    # maybe we want to use keywords after we receive the crawl results for better search and sorting?
    #keywords = models.ManyToManyField(Keyword, help_text="Select a keyword for this resource", blank=True)
    user = models.ForeignKey(User, related_name="crawl_requests_user", on_delete=models.CASCADE)
    created = models.DateTimeField("crawl request creation time", editable=False)
    modified = models.DateTimeField("crawl request modification time")
    model_name = models.CharField(max_length=128, blank=True)
    model_labels = models.CharField(max_length=128, blank=True)

    def save(self, *args, **kwargs):
        """ Update created and modified timestamps whenever a Crawl Request is saved """
        # only in the beginning (when the object doesn't exist yet) set the creation time.
        if not self.id:
            self.created = timezone.now()
        # set modified whenever an instance is saved
        self.modified = timezone.now()
        return super(CrawlRequest, self).save(*args, **kwargs)

    def get_absolute_url(self):
        """
        Returns the url to access a particular crawl request instance.
        Example: "crawl_request/3"
        """
        return reverse('mainapp_jobdetails', args=[str(self.id)])

    def __str__(self):
        """
        String for representing a Crawl Request.
        """
        return f'{self.id} {self.name}'


class Profile(models.Model):
    """
    The model to represent the user settings.
    """
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    s3_bucket = models.URLField("AWS S3 Bucket", default='', max_length=500, blank=True)
    api_key = models.CharField("API Key", max_length=512)
    api_secret = models.CharField("API Secret", max_length=512)
    num_crawlers = models.PositiveIntegerField("Number crawler instances", default=1)
    created = models.DateTimeField("profile creation time", editable=False)
    modified = models.DateTimeField("profile modification time")

    def save(self, *args, **kwargs):
        """ Update created and modified timestamps whenever settings are saved """
        # only in the beginning (when the object doesn't exist yet) set the creation time.
        if not self.id:
            self.created = timezone.now()
        # set modified whenever an instance is saved
        self.modified = timezone.now()
        return super(Profile, self).save(*args, **kwargs)

    def __str__(self):
        """
        String for representing a Profile.
        """
        return f'{self.id} {self.user.username}'

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        """ This method creates a profile instance as soon as a new user is created """
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        """ This method saves that profile instance to the database """
        instance.profile.save()

class MlModel(models.Model):
    """
    The model to represent the user Machine Learning Models.
    """
    name = models.CharField(max_length=128)
    #ml_model = models.FileField(upload_to='models/')
    labels = models.TextField(default='', max_length=100, blank=True)
    created = models.DateTimeField("model creation time", editable=False)
    modified = models.DateTimeField("model modification time")
    s3_location = models.URLField(default='', max_length=1000, blank=True)
    user = models.ForeignKey(User, related_name="ml_models_user", on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        """ Update created and modified timestamps whenever settings are saved """
        # only in the beginning (when the object doesn't exist yet) set the creation time.
        if not self.id:
            self.created = timezone.now()
        # set modified whenever an instance is saved
        self.modified = timezone.now()
        return super(MlModel, self).save(*args, **kwargs)

    def __str__(self):
        """
        String for representing a Profile.
        """
        return f'{self.id} {self.name}'
