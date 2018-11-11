import sys
from lxml import etree
from io import StringIO, BytesIO
import os.path
import urllib
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class User(object):
	def __init__(self, userID = '', itemsID = []):
		self.id = userID
		self.itemsID = itemsID
	def getString(self):
		return ''+str(self.id)+'\t'+','.join(str(x) for x in self.itemsID) 

class UsersCollection(object):
	def __init__(self):
		self.users = []
		self.usersID = []
		self.itemsID = []
		self.fileuser = 'user.csv'
		self.fileitems = 'items.csv'
	def addUser(self, user):
		if user.id not in self.usersID and user not in self.users:
			self.users.append(user)
			self.usersID.append(user.id)
	def addItemID(self, itemID):
		if itemID not in self.itemsID:
			self.itemsID.append(itemID)
	def existsUserID(self, userID):
		return userID in self.usersID
	def existsItemID(self, itemID):
		return itemID in self.itemsID
	def saveToDisk(self):
		with open(self.fileuser, 'w') as f:
			xxx = [x.getString() for x in self.users]
			f.write('\n'.join(xxx))
		with open(self.fileitems, 'w') as f:
			f.write('\n'.join(self.itemsID))
	def loadFromDisk(self):
		if os.path.isfile(self.fileuser): 
			with open(self.fileuser, 'r') as f:
				for line in f:
					userID, itemsID = line.split('\t')
					itemsID = itemsID.strip()
					itemsID = itemsID.split(',')
					self.addUser(User(userID, itemsID))
		if os.path.isfile(self.fileitems): 
			with open(self.fileitems, 'r') as f:
				itemsID = []
				for line in f:
					itemsID.append(line.strip())
				self.itemsID = itemsID

class Downloader(object):
	def __init__(self):
		self.driver = self.getWebdriver()
		self.counter = 0	
	def __del__(self):
		self.driver.close()
	def getSourcePage(self, url):
		self.counter += 1
		if self.counter > 10:
			self.driver.close()
			self.driver = self.getWebdriver()
			self.counter = 0
		self.driver.get(url)
		self.driver.get_screenshot_as_file("last_page.png")
		return self.driver.page_source
	def getWebdriver(self):
		WINDOW_SIZE = "1920,1080"
		prefs = {"profile.managed_default_content_settings.images": 2}
		chrome_options = Options()  
		chrome_options.add_experimental_option("prefs", prefs)
		#chrome_options.add_argument("--headless")  
		#chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
		return webdriver.Chrome(chrome_options=chrome_options) 	

def getAllReviewsLinkByItemID(itemID):
	base_link = 'https://www.amazon.com/gp/product/'
	temp_link = base_link + itemID
	page_source = downloader.getSourcePage(temp_link)
	tree = etree.parse(StringIO(page_source), parser)
	els = tree.xpath("//a[@data-hook='see-all-reviews-link-foot']")
	if len(els) == 0:
		return None
	else:
		return els[0].attrib['href']

def getAllUsersOnReviewPage(review_link):
	base_link = 'https://www.amazon.com'
	temp_link = base_link + review_link
	page_source = downloader.getSourcePage(temp_link)
	tree = etree.parse(StringIO(page_source), parser)
	els = tree.xpath("//a[@class='a-profile']")
	usersOnPage = []
	for i in els:
		usersOnPage.append(i.attrib['href'].split('/')[3])
	return usersOnPage

def getItemsByUserID(userID):
	nextPageToken = ''
	itemsID = []
	while nextPageToken != None:
		nextPageToken = nextPageToken.encode('ascii', 'ignore')
		url = 'https://www.amazon.com/profilewidget/timeline/visitor?nextPageToken={}&filteredContributionTypes=productreview&directedId={}'.format(urllib.quote(nextPageToken), userID)
		page_source = downloader.getSourcePage(url)
		print('url: ', url)
		tree = etree.parse(StringIO(page_source), parser)
		#print('JSON: ', tree.xpath("//text()")[0])
		response_dict = json.loads(tree.xpath("//text()")[0])
		contributions = response_dict['contributions']
		nextPageToken = response_dict['nextPageToken']
		itemsIDOnPage = [i[u'product'][u'asin'].encode('ascii', 'ignore') for i in contributions]
		itemsID.extend(itemsIDOnPage)
	return itemsID

def getUsersIDForItemID(itemID):
	print('itemID: ', itemID)
	review_link_general = getAllReviewsLinkByItemID(itemID)
	if review_link_general is None:
		return []
	base_link = 'https://www.amazon.com'
	print('itemID all reviews page: ', base_link+review_link_general)
	page_source = downloader.getSourcePage(base_link+review_link_general)
	tree = etree.parse(StringIO(page_source), parser)
	els = tree.xpath("//li[@data-reftag='cm_cr_arp_d_paging_btm']/a/text()")
	if len(els)> 1:
		total_pages = int(els[len(els)-1])
	else:
		total_pages = 1
	review_links = []
	to_be_replaced = 'ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews'
	for i in range(0, total_pages):
		replace_end = 'ref=cm_cr_arp_d_paging_btm_{}?ie=UTF8&reviewerType=all_reviews&pageNumber={}'.format(i+1,i+1)
		new_review_link = review_link_general.replace(to_be_replaced, replace_end)
		review_links.append(new_review_link)
	usersForItemID = []
	for review_link in review_links:
		usersForItemIDOnPage = getAllUsersOnReviewPage(review_link)
		usersForItemID.extend(usersForItemIDOnPage)
	return usersForItemID

ids='B07G8DLK1L,B00CKJG7NS,B07JQGNC39,B07J6Q2BPF,B01MZYT1SY,\
		B07GRRZ24K,B07GJ42DB2,B07HH5YV6K,B0713RDBL2,B07GQTRRFL,\
		B0777KZBVJ,B07G7F3CTB,B07H7NQR85,B07H7NQR85,B07HZ1DLHM,\
		B07G45PP87,B07FCQ6N8T,B07JD39DBM,B07F6HDYP5,B07DHSJB9C,\
		B07CZ1THSR,B07HFGXS1H,B07D57KLHK,B07HNJRW4S,B07G34H99N,\
		B07F9M89PY,B06XVMBJHS,B073CMZD1K,B07FS1DKJR,B07BVSZK4Z,\
		B0727YVQQ6,B07FK5HM8K,B0765D1SH9,B07F785JCV,B07CB3ZFWZ,\
		B07DJYH54N,B07HBDC5DS,B07DVZJB3D,B07CV4DNBT,B07BJFTH64,\
		B07B4HKLFK,B01LK0HQDW,B07FTNCB8C,B0777JD5DD,B01M9BFLVR,\
		B07FTVV16D,B07DR5BGR8,B07DWZPY23,B07FT36B8D,B07FSLHW1N,\
		B07DPNB6T5,B0798XT6JJ,B000Y1BGN0,B07FVSHQD7,B07FS1DKJR,\
		B075HJ8L9Z,B07D29TW3Z,B07F2NN6TM,B07G2SPZ6G,B076CK9F7P,\
		B07D7ZV9J9,B07GFVDSJX,B07HJYN8P3,B0753YMRCL,B07DJYH54N,\
		B07D7H5VKF,B071HW7WGS,B00TEPN5TA,B01FWIFRL6,B06Y1WYHZM,\
		B07J6FW99S,B00WSE81K2,B07HPCC5FS,B07H7PH33T,B07HXTCGQG,\
		B07JW4Y67L,B07JFW8YSP,B07JF2DSL5,B07G7F3CTB,B07CH81RGS,\
		B07FCQQXFL,B07JBC7YMY,B07G3JN3S4,B01MD2D7ZG,B07DX3BW39,\
		B079GCQN65,B07HKW2BS8'
ids = ids.replace('\t','').split(",")

user1 = User('amzn1.account.AGKWBHVKAXOGUB4X5BT2ZV2SJPZQ', ids)

parser = etree.HTMLParser()
downloader = Downloader()
col = UsersCollection()
col.loadFromDisk()
#col.add(user1)
# 'B07J6Q2BPF' usersID = getUsersIDForItemID('B07J6Q2BPF')
for itemID in user1.itemsID:
	if col.existsItemID(itemID):
		print('         ------- ITEM {} exists -------'.format(itemID))
		continue
	usersID = getUsersIDForItemID(itemID)
	users = []
	for userID in usersID:
		if col.existsUserID(userID):
			print('         ------- users {} exists -------'.format(userID))
			continue
		print('----------------------')
		print('----------------------')
		print('----------------------')
		print('itemID:', itemID, 'userID', userID)
		print('----')
		itemsID = getItemsByUserID(userID)
		col.addUser(User(userID, itemsID))
		col.saveToDisk()
	col.addItemID(itemID)
	col.saveToDisk()



# # ref=cm_cr_arp_d_paging_btm_1?ie=UTF8&reviewerType=all_reviews&pageNumber=1
# # '/Whiskey-Glass-Fashioned-Cocktail-Glassware/product-reviews/B01MD2D7ZG/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews'
# # '/Whiskey-Glass-Fashioned-Cocktail-Glassware/product-reviews/B01MD2D7ZG/ref=cm_cr_arp_d_paging_btm_3?ie=UTF8&reviewerType=all_reviews&pageNumber=3'
# # '/Whiskey-Glass-Fashioned-Cocktail-Glassware/product-reviews/B01MD2D7ZG/ref=cm_cr_arp_d_paging_btm_1?ie=UTF8&reviewerType=all_reviews&pageNumber=1'
# # ['/Whiskey-Glass-Fashioned-Cocktail-Glassware/product-reviews/B01MD2D7ZG/ref=cm_cr_arp_d_paging_btm_1?ie=UTF8&reviewerType=all_reviews&pageNumber=1', '/Whiskey-Glass-Fashioned-Cocktail-Glassware/product-reviews/B01MD2D7ZG/ref=cm_cr_arp_d_paging_btm_2?ie=UTF8&reviewerType=all_reviews&pageNumber=2', '/Whiskey-Glass-Fashioned-Cocktail-Glassware/product-reviews/B01MD2D7ZG/ref=cm_cr_arp_d_paging_btm_3?ie=UTF8&reviewerType=all_reviews&pageNumber=3', '/Whiskey-Glass-Fashioned-Cocktail-Glassware/product-reviews/B01MD2D7ZG/ref=cm_cr_arp_d_paging_btm_4?ie=UTF8&reviewerType=all_reviews&pageNumber=4', '/Whiskey-Glass-Fashioned-Cocktail-Glassware/product-reviews/B01MD2D7ZG/ref=cm_cr_arp_d_paging_btm_5?ie=UTF8&reviewerType=all_reviews&pageNumber=5', '/Whiskey-Glass-Fashioned-Cocktail-Glassware/product-reviews/B01MD2D7ZG/ref=cm_cr_arp_d_paging_btm_6?ie=UTF8&reviewerType=all_reviews&pageNumber=6', '/Whiskey-Glass-Fashioned-Cocktail-Glassware/product-reviews/B01MD2D7ZG/ref=cm_cr_arp_d_paging_btm_7?ie=UTF8&reviewerType=all_reviews&pageNumber=7']
# # rev_link = 'https://www.amazon.com/Whiskey-Glass-Fashioned-Cocktail-Glassware/product-reviews/B01MD2D7ZG/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews'

# r = requests.get(url = URL, params = PARAMS) 
# r
# # extracting data in json format 
# data = r.json() 

# URL = 'https://www.amazon.com/profilewidget/timeline/visitor?nextPageToken=&filteredContributionTypes=productreview%2Cglimpse%2Cideas&directedId=amzn1.account.AEBELQXS2ALPK5SW7QXNM56VRDOQ'


# getItemsByUserID('amzn1.account.AEBELQXS2ALPK5SW7QXNM56VRDOQ')


# nextPageToken = response['nextPageToken'].encode('ascii', 'ignore')
# PARAMS = {'nextPageToken':nextPageToken, 'filteredContributionTypes':'productreview', 'directedId':userID}
# r = requests.get(url = URL, headers = headers, params = PARAMS) 
# response = json.loads(r.text)
# print(response['nextPageToken'].encode('ascii', 'ignore'))
# print('contributions: ', len(response['contributions']))
# 	# HTTP REQUETS
# 	# URL = 'https://www.amazon.com/profilewidget/timeline/visitor'
# 	# headers = {'authority': 'www.amazon.com',
# 	# 			'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
# 	# 			'accept-encoding':'gzip, deflate, br',
# 	# 			'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
# 	# 			}
# 	# nextPageToken = ''
# 	# itemsID = []
# 	# while nextPageToken != None:
# 	# 	nextPageToken = nextPageToken.encode('ascii', 'ignore')
# 	# 	PARAMS = {'nextPageToken':nextPageToken, 'filteredContributionTypes':'productreview', 'directedId':userID}
# 	# 	response = requests.get(url = URL, headers = headers, params = PARAMS) 
# 	# 	print('url: ', response.request.url)
# 	# 	print('status: ', response.status_code)
# 	# 	if response.status_code !=200:
# 	# 		nextPageToken=None
# 	# 		continue	
# 	# 	response_dict = json.loads(response.text)
# 	# 	contributions = response_dict['contributions']
# 	# 	nextPageToken = response_dict['nextPageToken']
# 	# 	itemsIDOnPage = [i[u'product'][u'asin'].encode('ascii', 'ignore') for i in contributions]
# 	# 	itemsID.extend(itemsIDOnPage)
# 	# return itemsID