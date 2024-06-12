import chromedriver_autoinstaller

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import tag
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from catalog.models import User

class E2ETests(StaticLiveServerTestCase):
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

    @tag('e2e')
    def test_home_not_authenticated(self):
        self.selenium.get(f'{self.live_server_url}/')

        self.assertIn("Bib Xulambis", self.selenium.title)
        
        main_header = self.selenium.find_element(By.TAG_NAME, 'h1').text
        self.assertIn("Bib", main_header)
        
        welcome_message = self.selenium.find_element(By.TAG_NAME, 'p').text
        self.assertIn("Bem-vindo ao site da biblioteca municipal de Xulambis", welcome_message)

    @tag('e2e')
    def test_user_login_is_success(self):
        self.selenium.get(f'{self.live_server_url}/accounts/login/')

        User.objects.create_user(username='testuser', password='secret')

        username_field = self.selenium.find_element(By.NAME, 'username')
        password_field = self.selenium.find_element(By.NAME, 'password')
        submit_button = self.selenium.find_element(By.XPATH, "//input[@type='submit']")

        username_field.send_keys('testuser')
        password_field.send_keys('secret')

        submit_button.click()
        
        self.assertIn("catalog/", self.selenium.current_url)

    @tag('e2e')
    def test_user_login_is_fail(self):
        self.selenium.get(f'{self.live_server_url}/accounts/login/')

        User.objects.create_user(username='testuser', password='secret')

        username_field = self.selenium.find_element(By.NAME, 'username')
        password_field = self.selenium.find_element(By.NAME, 'password')
        submit_button = self.selenium.find_element(By.XPATH, "//input[@type='submit']")

        username_field.send_keys('testuserfailed')
        password_field.send_keys('secret')

        submit_button.click()

        error_message = self.selenium.find_element(By.XPATH, "//p[contains(text(), 'Usuário ou senha incorretos. Tente novamente.')]")

        self.assertIn("accounts/login/", self.selenium.current_url)
        self.assertIsNotNone(error_message)
