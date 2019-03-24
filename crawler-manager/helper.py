import settings
from urllib.parse import urlparse


def validateChildURLs(somain_name, child_urls):
  pass
  return []

def updateRedis(main_url, s3Link, child_urls):
  pass
  return


def get_domain_name(url):
  try:
    results = get_sub_domain_name(url).split('.')
    return results[-2] + '.' + results[-1]
  except:
    return ''


def get_sub_domain_name(url):
  try:
    return urlparse(url).netloc
  except:
    return ''