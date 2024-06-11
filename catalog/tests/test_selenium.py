# tests.py em um dos seus aplicativos Django

from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from django.conf import settings
import chromedriver_autoinstaller

class MySeleniumTests(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        chromedriver_autoinstaller.install()
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        cls.selenium = webdriver.Chrome(options=chrome_options)
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_example(self):
        #pra testar se seu selenium ta funcionando
        self.selenium.get(f'{self.live_server_url}/')
        self.assertIn("Bib Xulambis", self.selenium.title)
