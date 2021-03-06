'''
Created on 7 nov. 2013

@author: Alexandre Bonhomme
'''
from wsgi.fr.blckshrk.zaramining.core.downloader import Downloader
from wsgi.fr.blckshrk.zaramining.core.product import Product
from wsgi.fr.blckshrk.zaramining.scrapers.scraper import Scraper
from wsgi.fr.blckshrk.zaramining.scrapers.zara.zara_browser import ZaraBrowser
import errno
import logging as log
import os
import time

class ZaraScrape(Scraper):

    BRAND_NAME = 'Zara'
    PAGE_BASE = 'http://www.zara.com/fr/'

    def __init__(self, lang):
        self.lang = lang
        self.downloader = Downloader()

    def setConfig(self, section, subsection, productType, bodyPart):
        self.section = section
        self.subsection = subsection
        self.type = productType
        self.bodies = bodyPart

        self.dl_folder = self.DL_FOLDER_PATH_BASE + self.lang + '/' + section + '/' + subsection + '/'
        # Create folder if is not existing
        try:
            os.makedirs(self.dl_folder)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    '''
        Perfom the scraping on Zara website
    '''
    def run(self, usePlainImage = True, download = False):
        log.info('-- Starting scraping --')

        home = self.downloader.getFile(self.PAGE_BASE + self.lang + '/')
        browser = ZaraBrowser(home)

        url = browser.getMenuLinkFromName(self.section)
        try:
            browser.goTo(url, 5)
        except:
            log.warning("Unable to get the page '" + url + "'. Omitting.")
            return []

        url = browser.getMenuLinkFromName(self.subsection)
        try:
            browser.goTo(url, 5)
        except:
            log.warning("Unable to get the page '" + url + "'. Omitting.")
            return []

        i = 0
        itemList = []
        for item in browser.getProductsList():
            log.debug('zzZZZZzzz')
            time.sleep(5) # let's do it cool

            try:
                browser.goTo(item['url'])
            except:
                log.warning("FAIL : Unable to download '" + item['name'] + "'. Omitting.")
                continue

            imgUrl = browser.getProductImageLink(usePlainImage)
            if imgUrl is None:
                log.info('FAIL : Unable to get product image for "' + item['name'] + '". Omitting.')
                continue

            if download:
                imgFilename = str(i) + '-' + item['name']
                log.info('Downloading ' + imgFilename + '...')
                self.downloader.writeFile(imgUrl, self.dl_folder + imgFilename)

            color = browser.getProductColor()

            log.info('SUCCES : Product "' + item['name'] + '" scraping done.')
            itemList.append(Product(item['name'], self.BRAND_NAME, color, imgUrl, self.type, self.bodies))
            i += 1

        log.info('-- Ending scraping --')
        log.info('-- ' + str(i) + ' images was scraped --')

        return itemList
