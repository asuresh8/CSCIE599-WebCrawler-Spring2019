import flask
import requests
import aiohttp
import asyncio
from parsel import Selector
import time
import uuid
import os
from redis_connect import testConnectionRedis, testLocalRedis, getVariable, setVariable
from collections import deque


def run_main():
    # The environment variable for the JOB_ID is set by Kubernetes, which recieves 
    # this JOB_ID from the main application
    # Number of crawlers also set by the queue
    # jobID = os.environ['JOB_ID']
    # numberOfCrawlers = os.environ['NUM_of_CRAWLERS']

    #example ID:
    jobID = uuid.uuid4()

    print("Executing Job: %s" % jobID)

    #Get the metadata regarding this job from mysql
    # jobMetaData = getJobMetadata(jobID)
    jobMetaData = [('jobID123','http://recurship.com/','img'),('jobID123','https://iamtrask.github.io/','img')]
    crawlURLs = []
    for (jobid, url, file_type) in jobMetaData:
      print("{} needs to visit url {} and look at {} files".format(
        jobid, url, file_type))
    crawlURLs.append(url)

    urlsQueue = deque(crawlURLs)

    #Function to create n number of crawlers as defined by numberOfCrawlers

    counter = 0
    visitedUrls = []

    #Counter less than 3 is there for testing to ensure an infinite loop is not encountered, is there a depth limit?
    while urlsQueue.__len__ != 0 and counter < 2:
        crawlurl = urlsQueue.popleft()
        print(crawlurl)

        # Call a function that assigns the above url to a crawler and appends the child urls to the queue in response
        response = requests.get(crawlurl)
        selector = Selector(response.text)
        child_urls = selector.xpath('//a/@href').getall()

        #append visited url
        visitedUrls.append(crawlurl)
        print("Visited URLs : " + str(visitedUrls))

        #Removing urls that have already been visited
        notVisitedChildUrls = list(set(child_urls) - set(visitedUrls))
        urlsQueue.append(notVisitedChildUrls)

        #Setting key as url, and value as child urls in redis (checking write)
        setVariable(crawlurl, notVisitedChildUrls)

        #Getting url from redis (checking read)
        print(getVariable(crawlurl))

        counter = counter + 1

        print ("All done !")
        end = time.time()
        print("Time taken in seconds : ", (end-start))


if __name__ == '__main__':
    run_main()