from google.cloud import storage
import posixpath
import urllib

#Expands all relative links to absolute urls
def expand_url(home, url):
    join = urllib.parse.urljoin(home,url)
    url2 = urllib.parse.urlparse(join)
    path = posixpath.normpath(url2[2])

    return urllib.parse.urlunparse(
        (url2.scheme, url2.netloc, path, url2.params, url2.query, url2.fragment)
    )


def get_domain_name(url):
    parsed_uri = urllib.parse.urlparse(url)
    return '{uri.netloc}'.format(uri=parsed_uri)

def get_root_url(url):
    parsed_uri = urllib.parse.urlparse(url)
    return '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

def is_absolute_url(url):
    return bool(urllib.parse.urlparse(url).netloc)


def is_root_url(url):
    return urllib.parse.urlparse(url).path == '/'


def strip_protocol_from_url(url):
    return url.replace('https://', '')\
        .replace('http://', '')\
        .replace('ftp://', '')\
        .replace('www.', '')


def upload_public_file(file_path, bucket, key):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket)
    blob = bucket.blob(key)
    blob.upload_from_filename(file_path)
    blob.make_public()
    return blob.public_url