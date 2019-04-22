import posixpath
import urllib
import logging

import crawler_manager_context as context

logging.basicConfig(level=logging.INFO)
#Expands all relative links to absolute urls
def expand_url(home, url):
    join = urllib.parse.urljoin(home,url)
    url2 = urllib.parse.urlparse(join)
    path = posixpath.normpath(url2[2])

    return urllib.parse.urlunparse(
        (url2.scheme, url2.netloc, path, url2.params, url2.query, url2.fragment)
    )


def get_domain_name(url):
    logging.info('uri to parse %s', url)
    parsed_uri = urllib.parse.urlparse(url)
    logging.info('uri === %s', parsed_uri)
    return '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)


def is_absolute_url(url):
    return bool(urllib.parse.urlparse(url).netloc)


def strip_protocol_from_url(url):
    return url.replace('https://', '')\
        .replace('http://', '')\
        .replace('ftp://', '')\
        .replace('www.', '')
