from bs4 import BeautifulSoup as bs
import requests
import os
import sys
import argparse
import gettext
import logging
import logging.handlers
import urllib
from datetime import datetime

domain="https://www.torrents9.pw"
search_url="%s/recherche" % (domain)

logger = logging.getLogger("default")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s | %(levelname)8s | %(message)s")

stStdout = logging.StreamHandler()
stStdout.setFormatter(formatter)
logger.addHandler(stStdout)

appDir= os.environ['HOME']+"/.torrent9"
logsDir = appDir + "/logs"
if not os.path.isdir(logsDir):
    if not os.path.isdir(appDir):
        os.mkdir(appDir)
    os.mkdir(logsDir)

stLogfile = logging.handlers.RotatingFileHandler(logsDir+'/log', maxBytes=256*1024, backupCount=10)
stLogfile.setFormatter(formatter)
#stLogfile.doRollover()
logger.addHandler(stLogfile)



def findAllTorrents(url):
    mustPaginate = False
    links = []
    haveToContinue = True
    while haveToContinue:
        logger.debug("connect")
        pageSoup = bs(requests.get(url).content, 'html.parser')
        # We search all the link
        for i, aTd in enumerate(pageSoup.findAll('td')):
            aLink = aTd.find('a')
            logger.debug("link to torrent page")
            logger.debug(aLink)
            if aLink :
                href = aLink.get('href')
                nom = aLink.text
                if href:
                    logger.debug("searchLinksInUrl : analyze url "+href)
                    # And perform a link target matching
                    link = {"name": nom, "url" :"%s/%s" % (domain, href)}
                    links.append(link)
        if mustPaginate :
            aListNext = pageSoup.find('ul', attrs={'class' : 'pagination'})
            aNext = aListNext.findAll('li')
            haveToContinue = aNext != None
            if  haveToContinue :
                haveToContinue = aNext.find("a") != None
            if  haveToContinue :
                aNext.find("a") != None
                url = "%s/%s"  % (domain, aNext.find("a").get("href"))
                logger.debug("NEXT URL  : "+url )
        else : 
            haveToContinue = False   
    return links

def analyzePageTorrent(link) :
    pageSoup = bs(requests.get(link['url']).content)
    linkTorrent = pageSoup.find("a", attrs = {'class':"download"})
    logger.debug("links for torrent download forms")
    logger.debug(linkTorrent)
    if linkTorrent :
        urlTorrent = "%s/%s" % (domain, linkTorrent.get('href'))
        torrentFile = requests.get(urlTorrent).content
        fp = open("%s.torrent" % (link['name']), 'w')
        fp.write(torrentFile)
        fp.close()





if __name__ == "__main__":
    mySearch = "%s/%s" % (search_url, urllib.quote_plus(sys.argv[1]))
    print mySearch
    torrentsLinks = findAllTorrents(mySearch)
    for link in torrentsLinks:
        analyzePageTorrent(link)
