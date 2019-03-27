import settings
from urllib.parse import urlparse, urljoin, urlunparse
import posixpath
from redis_connect import setVariable, getVariable
 
#Expands all relative links to absolute urls
def expand_url(home, url):
    join = urljoin(home,url)
    url2 = urlparse(join)
    path = posixpath.normpath(url2[2])
 
    return urlunparse(
        (url2.scheme,url2.netloc,path,url2.params,url2.query,url2.fragment)
        )

# Removes child urls that are already in the queue, or being currently processed, or have been already processed, or have a separate 
# domain than the domain name entered
def validateChildURLs(domain_name, main_url, child_urls):
  validatedURLs = []
  for url in child_urls:
    absolute_url = expand_url(main_url, url)
    if absolute_url in settings.queuedURLs.queue:
      continue
    if absolute_url in settings.processingURLs:
      continue
    if absolute_url in settings.processedURLs:
      continue
    if domain_name not in absolute_url:
      continue
    validatedURLs.append(absolute_url)
  return validatedURLs

#update redis, add information for a crawled url
def updateRedis(main_url, s3Link, child_urls):
  parentCrawl = {"parentURL": main_url,"S3": s3Link, "childURLs": child_urls}
  setVariable(main_url,parentCrawl)
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

# settings.init()
# print(validateChildURLs('recurship.com','https://www.recurship.com', ['https://wikipedia.com','https://www.youtube.com','/about','home']))