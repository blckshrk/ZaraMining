'''
Created on 24 oct. 2013

@author: Alexandre Bonhomme
'''

from bs4 import BeautifulSoup
from wsgi.fr.blckshrk.zaramining.core.downloader import Downloader
from wsgi.fr.blckshrk.zaramining.scrapers.browser import Browser
import logging as log
import re

class ZaraBrowser(Browser):

    '''
    @param page: Just a string with html code
    '''
    def __init__(self, page):
        self.downloader = Downloader()
        self.soup = BeautifulSoup(page)

    def goTo(self, url, timeRetrying = None):
        try:
            page = self.downloader.getFile(url, timeRetrying)
        except:
            raise
        else:
            self.soup = BeautifulSoup(page)

    '''
    Menu section parsing
    '''
    def getMenu(self, bSubmenu = False):
        if bSubmenu:
            menu = self.soup.find(id = 'mainNavigationMenu').find('ul', attrs = {'class': 'bSubmenu'})
        else:
            menu = self.soup.find(id = 'mainNavigationMenu')

        return menu

    def getMenuEntries(self, bSubmenu = False):
        menu = self.getMenu(bSubmenu)
        entries = menu.find_all('a')

        return entries

    def getMenuLinkFromName(self, name):
        menu = self.getMenu()
        link = menu.find('a', text = re.compile(r'\s+' + name, re.I)).get('href')

        return link

    '''
    Products section parsing
    '''
    def getProductsList(self):
        product_list = self.soup.find(id = 'product-list')
        product_list_info = product_list.find_all('div', attrs = {'class': 'product-info'})

        dummy = []
        for product in product_list_info:
            product_link = product.find('a')

            dummy.append({'name': product_link.get_text(),
                          'url': product_link.get('href')})

        return dummy

    '''
    Product page parsing
    '''
    def getProductImageLink(self, usePlainImage):
        if usePlainImage:
            return self.getProductPlainImageLink()
        else:
            return self.getProductFullImageLink()

    '''
    @warning: May do not have a return value
    @return: 'plain' image or None
    '''
    def getProductPlainImageLink(self):
        container = self.soup.find('div', attrs = {'class': 'bigImageContainer'})

        try:
            imageSrc = container.find('div', attrs = {'class': 'plain'}) \
                                .find('img', attrs = {'class': 'image-big'}) \
                                .get('src')
        except AttributeError:
            log.warning('No "plain" image found for this product.')
        else:
            if not re.match('^http://', imageSrc, re.I):
                return 'http:' + imageSrc
            else:
                return imageSrc

    '''
    @warning: May do not have a return value
    @return: 'full' image or None
    '''
    def getProductFullImageLink(self):
        container = self.soup.find('div', attrs = {'class': 'bigImageContainer'})

        try:
            imageSrc = container.find('div', attrs = {'class': 'full'}) \
                                .find('img', attrs = {'class': 'image-big'}) \
                                .get('src')
        except AttributeError:
            log.warning('No "full" image found for this product.')
        else:
            if not re.match('^http://', imageSrc, re.I):
                return 'http:' + imageSrc
            else:
                return imageSrc

    def getProductColor(self):
        container = self.soup.find('form', attrs = {'name': 'itemAdd'}) \
                             .find('div', attrs = {'class': 'colors'}) \
                             .find('label', attrs = {'class': 'selected'})
        color_name = container.find('span').get_text()
        color_value = container.get('data-colorcode')

        return {'name': color_name, 'value': color_value}

