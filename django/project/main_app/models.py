from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User


'''
class Keyword(models.Model):
    """
    A simple model to create keywords for better sorting and reporting
    """
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        """
        String for representing a Keyword.
        """
        return f'{self.name}'
'''

class CrawlRequest(models.Model):
    """
    The model to represent a crawl request.
    """
    CRAWLTYPES = (
        (1, 'All content from a single domain'),
        (2, 'Content from multiple URLs')
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
    # maybe we want to use keywords after we receive the crawl results for better search and sorting?
    #keywords = models.ManyToManyField(Keyword, help_text="Select a keyword for this resource", blank=True)
    user = models.ForeignKey(User, related_name="crawl_requests_user", on_delete=models.CASCADE)
    created = models.DateTimeField("crawl request creation time", editable=False)
    modified = models.DateTimeField("crawl request modification time")

    def save(self, *args, **kwargs):
        """ Update created and modified timestamps whenever a Crawl Request is saved """
        # only in the beginning (when the object doesn't exist yet) set the creation time.
        if not self.id:
            self.created = timezone.now()
        # set modified whenever an instance is saved
        self.modified = timezone.now()
        return super(Crawl, self).save(*args, **kwargs)

    def get_absolute_url(self):
        """
        Returns the url to access a particular crawl request instance.
        Example: "crawl/3"
        """
        return reverse('crawl', args=[str(self.id)])

    def __str__(self):
        """
        String for representing a Crawl Request.
        """
        return f'{self.id} {self.name} ({self.link})'
