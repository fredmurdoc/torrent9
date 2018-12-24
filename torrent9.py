from bs4 import BeautifulSoup as bs
import requests
import os
import sys
import argparse
import gettext
import logging
import logging.handlers
import urllib
import re
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

headers = { 'User-Agent' : 'Mozilla/5.0' }

def findAllTorrents(url):
    mustPaginate = False
    links = []
    haveToContinue = True
    while haveToContinue:
        logger.debug("connect")
        pageSoup = bs(requests.get(url, headers=headers).content, 'html.parser')
        # We search all the link
        for i, aTd in enumerate(pageSoup.findAll('td')):
            aLink = aTd.find('a')
            logger.debug("link to torrent page")
            logger.debug(aLink)
            if aLink :
                href = aLink.get('href')
                nom = aLink.text
                if href:
                    nurl = "%s/%s" % (domain, href)
                    logger.debug("searchLinksInUrl : analyze url "+nurl)
                    # And perform a link target matching
                    link = {"name": nom, "url" : nurl}
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

def analyseLink(link, title,download_dir):
    logger.debug("link to analyze : %s for TITLE %s" % (link, title))
    if link[0:len("magnet:")] == "magnet:":
        logger.debug("magnet link")
        destFile = "%s/MAGNETS.html" % (download_dir)
        logger.debug("save to %s" % (destFile))
        fp = open(destFile, "a")
        fp.write("<a href=\"%s\">%s</a><br/>\n" % (link, title))
        fp.close()
    else:             
        index = link.find("protege-liens.net")
        if index > 0:
            logger.debug("link is protected")
            reallink = link[index + len("protege-liens.net"):]
            logger.debug(reallink)
            if reallink :
                 urlTorrent = "%s%s" % (domain, reallink)
                 logger.debug("urlTorrent : %s" %(urlTorrent))
                 torrentFile = requests.get(urlTorrent).content
                 fp = open("%s/%s.torrent" % (download_dir, title), 'w')
                 fp.write(torrentFile)
                 fp.close()

def analyzePageAndDowloadTorrent(link, download_dir) :
    pageSoup = bs(requests.get(link['url'], headers=headers).content)
    lfp = open("test.html", "w")
    lfp.write(str(pageSoup))
    lfp.close()
    linksTorrents = pageSoup.findAll("a", attrs = {'class':"download"})
    logger.debug("links for torrent download forms")
    logger.debug(linksTorrents)
    for linkTorrent in linksTorrents:
        reallink = linkTorrent.get('href')             
        analyseLink(reallink, link['name'], download_dir)

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-s', dest='search', help='proceed only a search')
parser.add_argument('-t', dest='title', help='title to download')
parser.add_argument('-d', dest='download_dir', help='download directory', default='torrents')



args = parser.parse_args()
print(args)
if __name__ == "__main__":
    if args.search:
        mySearch = "%s/%s" % (search_url, urllib.quote_plus(args.search))
        print mySearch
        torrentsLinks = findAllTorrents(mySearch)
        print("\n".join(map(lambda x : x['name'], torrentsLinks)))
    if args.title:
        mySearch = "%s/%s" % (search_url, urllib.quote_plus(args.title))
        print mySearch
        torrentsLinks = findAllTorrents(mySearch)
        print("\n".join(map(lambda x : x['name'], torrentsLinks)))

        if not(os.path.exists(args.download_dir)):
            os.mkdir(args.download_dir)
        for link in torrentsLinks:
            analyzePageAndDowloadTorrent(link, args.download_dir)
