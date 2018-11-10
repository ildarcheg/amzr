import base64
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from urllib import quote
from xvfbwrapper import Xvfb
import sys
import codecs
import binascii
import os
import datetime

from lxml import etree
from io import StringIO, BytesIO

print(sys.getdefaultencoding())
reload(sys)
sys.setdefaultencoding("utf-8")
print(sys.getdefaultencoding())

def get_driver():
	url = "http://www.forum.mista.ru/index.php"
	driver = webdriver.Chrome()
	return driver

ids='B07G8DLK1L,B00CKJG7NS,B07JQGNC39,B07J6Q2BPF,B01MZYT1SY,B07GRRZ24K,B07GJ42DB2,B07HH5YV6K,B0713RDBL2,B07GQTRRFL,B0777KZBVJ,B07G7F3CTB,B07H7NQR85,B07H7NQR85,B07HZ1DLHM,B07G45PP87,B07FCQ6N8T,B07JD39DBM,B07F6HDYP5,B07DHSJB9C,B07CZ1THSR,B07HFGXS1H,B07D57KLHK,B07HNJRW4S,B07G34H99N,B07F9M89PY,B06XVMBJHS,B073CMZD1K,B07FS1DKJR,B07BVSZK4Z,B0727YVQQ6,B07FK5HM8K,B0765D1SH9,B07F785JCV,B07CB3ZFWZ,B07DJYH54N,B07HBDC5DS,B07DVZJB3D,B07CV4DNBT,B07BJFTH64,B07B4HKLFK,B01LK0HQDW,B07FTNCB8C,B0777JD5DD,B01M9BFLVR,B07FTVV16D,B07DR5BGR8,B07DWZPY23,B07FT36B8D,B07FSLHW1N,B07DPNB6T5,B0798XT6JJ,B000Y1BGN0,B07FVSHQD7,B07FS1DKJR,B075HJ8L9Z,B07D29TW3Z,B07F2NN6TM,B07G2SPZ6G,B076CK9F7P,B07D7ZV9J9,B07GFVDSJX,B07HJYN8P3,B0753YMRCL,B07DJYH54N,B07D7H5VKF,B071HW7WGS,B00TEPN5TA,B01FWIFRL6,B06Y1WYHZM,B07J6FW99S,B00WSE81K2,B07HPCC5FS,B07H7PH33T,B07HXTCGQG,B07JW4Y67L,B07JFW8YSP,B07JF2DSL5,B07G7F3CTB,B07CH81RGS,B07FCQQXFL,B07JBC7YMY,B07G3JN3S4,B01MD2D7ZG,B07DX3BW39,B079GCQN65,B07HKW2BS8'
ids = ids.split(",")

#link = 'https://www.amazon.com/gp/product/B01MD2D7ZG'

driver = get_driver()
parser = etree.HTMLParser()

def getAllReviewsLinkByItemID(itemID):
	base_link = 'https://www.amazon.com/gp/product/'
	temp_link = base_link + itemID
	driver.get(temp_link)
	tree = etree.parse(StringIO(driver.page_source), parser)
	els = tree.xpath("//a[@data-hook='see-all-reviews-link-foot']")
	if len(els) == 0:
		return None
	else:
		return els[0].attrib['href']

def getAllUsersOnReviewPage(review_link):
	base_link = 'https://www.amazon.com'
	temp_link = base_link + review_link
	driver.get(temp_link)
	els = tree.xpath("//a[@class='a-profile']")
	return [i.attrib['href'].split('/')[3] for i in els]

base_link = 'https://www.amazon.com'
rev_links = [base_link + i for i in sublinks]

rev_link = 'https://www.amazon.com/Whiskey-Glass-Fashioned-Cocktail-Glassware/product-reviews/B01MD2D7ZG/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews'
driver.get(rev_link)
html = driver.page_source
tree   = etree.parse(StringIO(html), parser)
print(rev_link)
els = tree.xpath("//a[@class='a-profile']")
[base_link + i.attrib['href'] for i in els]

def getUsersForItemID(itemID):

review_link = getAllReviewsLinkByItemID(itemID)
base_link = 'https://www.amazon.com'
driver.get(base_link+review_link)
els = tree.xpath("//li[@data-reftag='cm_cr_arp_d_paging_btm']/a/text()")
if len(els)> 1:
	total_pages = int(els[len(els)-1])
else:
	total_pages = 1
review_links = []
to_be_replaced = 'ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews'
for i in range(0, total_pages):
	replace_end = 'ref=cm_cr_arp_d_paging_btm_{}?ie=UTF8&reviewerType=all_reviews&pageNumber={}'.format(i+1,i+1)
	new_review_link = review_link.replace(to_be_replaced, replace_end)
	review_links.append(new_review_link)

print(rev_link)

getUsersForItemID('B01MD2D7ZG')
ref=cm_cr_arp_d_paging_btm_1?ie=UTF8&reviewerType=all_reviews&pageNumber=1
'/Whiskey-Glass-Fashioned-Cocktail-Glassware/product-reviews/B01MD2D7ZG/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews'
'/Whiskey-Glass-Fashioned-Cocktail-Glassware/product-reviews/B01MD2D7ZG/ref=cm_cr_arp_d_paging_btm_3?ie=UTF8&reviewerType=all_reviews&pageNumber=3'
'/Whiskey-Glass-Fashioned-Cocktail-Glassware/product-reviews/B01MD2D7ZG/ref=cm_cr_arp_d_paging_btm_1?ie=UTF8&reviewerType=all_reviews&pageNumber=1'