import crawler_manager_context as context
from urllib.parse import urlparse, urljoin, urlunparse
import posixpath
 
#Expands all relative links to absolute urls
def expand_url(home, url):
    join = urljoin(home,url)
    url2 = urlparse(join)
    path = posixpath.normpath(url2[2])
 
    return urlunparse(
        (url2.scheme, url2.netloc, path, url2.params, url2.query, url2.fragment)
    )

def get_domain_name(url):
    try:
        results = get_sub_domain_name(url).split('.')
        return results[-2] + '.' + results[-1]
    except:
        return ''

def is_absolute_url(url):
    return bool(urlparse(url).netloc)
