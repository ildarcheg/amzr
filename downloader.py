from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pyvirtualdisplay import Display

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
		return self.driver.page_source
	def getWebdriver(self):
		WINDOW_SIZE = "1920,1080"
		prefs = {"profile.managed_default_content_settings.images": 2}
		chrome_options = Options()  
		chrome_options.add_experimental_option("prefs", prefs)
		#chrome_options.add_argument("--headless")  
		#chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
		return webdriver.Chrome(chrome_options=chrome_options) 	


d = Downloader()
d.driver.get("https://www.google.com")
d.driver.get_screenshot_as_file("capture.png")
d.driver.close()