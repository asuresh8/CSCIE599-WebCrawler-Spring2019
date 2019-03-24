# settings.py
# contains all global variables shared amongst modules
import queue

def init():

    #List of urls that need be crawled
    global queuedURLs
    queuedURLs = queue.Queue()

    #Set of crawlers, represented by ips:ports/dns
    global crawlerSet
    crawlerSet = set()

    #Set of urls currently being crawled by the crawlers
    global processingURLs
    processingURLs = set()

    #Ser of processed URLs
    global processedURLs
    processedURLs = set()
