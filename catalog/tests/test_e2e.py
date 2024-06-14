import chromedriver_autoinstaller

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import Permission
from django.test import tag
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from catalog.models import User, Genre

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
    def test_user_login_success(self):
        username = 'testuser'
        password = 'secret'
        self.test_user = User.objects.create_user(username=username, password=password)

        self.selenium.get(f'{self.live_server_url}/accounts/login/')

        username_field = self.selenium.find_element(By.NAME, 'username')
        password_field = self.selenium.find_element(By.NAME, 'password')
        submit_button = self.selenium.find_element(By.XPATH, "//input[@type='submit']")

        username_field.send_keys(username)
        password_field.send_keys(password)

        submit_button.click()
        
        self.assertIn("catalog/", self.selenium.current_url)

    @tag('e2e')
    def test_user_login_fail(self):
        self.selenium.get(f'{self.live_server_url}/accounts/login/')

        username_field = self.selenium.find_element(By.NAME, 'username')
        password_field = self.selenium.find_element(By.NAME, 'password')
        submit_button = self.selenium.find_element(By.XPATH, "//input[@type='submit']")

        username_field.send_keys('wronguser')
        password_field.send_keys('wrongpassword')

        submit_button.click()

        error_message = self.selenium.find_element(By.XPATH, "//p[contains(text(), 'Usuário ou senha incorretos. Tente novamente.')]")

        self.assertIn("accounts/login/", self.selenium.current_url)
        self.assertIsNotNone(error_message)

    @tag('e2e')
    def test_login_and_create_author(self):
        username = 'testuser'
        password = 'secret'
        self.test_user = User.objects.create_user(username=username, password=password)
        permission = Permission.objects.get(name='Can add author')
        self.test_user.user_permissions.add(permission)
        permission = Permission.objects.get(name='Can change author')
        self.test_user.user_permissions.add(permission)
        permission = Permission.objects.get(name='Can delete author')
        self.test_user.user_permissions.add(permission)
        permission = Permission.objects.get(name='Can view author')
        self.test_user.user_permissions.add(permission)
        self.test_user.is_staff = True
        self.test_user.save()

        self.selenium.get(f'{self.live_server_url}/accounts/login/')

        # Login
        username_field = self.selenium.find_element(By.NAME, 'username')
        password_field = self.selenium.find_element(By.NAME, 'password')
        submit_button = self.selenium.find_element(By.XPATH, "//input[@type='submit']")

        username_field.send_keys(username)
        password_field.send_keys(password)

        submit_button.click()

        # Go to "Create author" page
        create_author_button = self.selenium.find_element(By.XPATH, "//a[contains(@href,'/catalog/author/create')]")
        create_author_button.click()
        
        # Fill form
        first_name_field = self.selenium.find_element(By.NAME, 'first_name')
        last_name_field = self.selenium.find_element(By.NAME, 'last_name')
        date_of_birth_field = self.selenium.find_element(By.NAME, 'date_of_birth')

        first_name_field.send_keys('Douglas')
        last_name_field.send_keys('Adams')
        date_of_birth_field.send_keys('11/03/1952')

        submit_button = self.selenium.find_element(By.XPATH, "//input[@type='submit']")

        submit_button.click()

        # Asserts
        title = self.selenium.find_element(By.TAG_NAME, 'h1').text
        self.assertIn('Douglas Adams', title)
        
        date = self.selenium.find_element(By.TAG_NAME, 'p').text
        self.assertIn('Data de Nascimento: 11 de Março de 1952', date)

    @tag('e2e')
    def test_login_and_create_book(self):
        username = 'testuser'
        password = 'secret'
        self.test_user = User.objects.create_user(username=username, password=password)
        permission = Permission.objects.get(name='Can add author')
        self.test_user.user_permissions.add(permission)
        permission = Permission.objects.get(name='Can change author')
        self.test_user.user_permissions.add(permission)
        permission = Permission.objects.get(name='Can delete author')
        self.test_user.user_permissions.add(permission)
        permission = Permission.objects.get(name='Can view author')
        self.test_user.user_permissions.add(permission)

        permission = Permission.objects.get(name='Can add book')
        self.test_user.user_permissions.add(permission)
        permission = Permission.objects.get(name='Can change book')
        self.test_user.user_permissions.add(permission)
        permission = Permission.objects.get(name='Can delete book')
        self.test_user.user_permissions.add(permission)
        permission = Permission.objects.get(name='Can view book')
        self.test_user.user_permissions.add(permission)

        self.genre1 = Genre.objects.create(name='Fantasia Paranormal')
        self.genre2 = Genre.objects.create(name='Romance')

        self.test_user.is_staff = True
        self.test_user.save()

        self.selenium.get(f'{self.live_server_url}/accounts/login/')

        # Login
        username_field = self.selenium.find_element(By.NAME, 'username')
        password_field = self.selenium.find_element(By.NAME, 'password')
        submit_button = self.selenium.find_element(By.XPATH, "//input[@type='submit']")

        username_field.send_keys(username)
        password_field.send_keys(password)

        submit_button.click()

        # Go to "Create author" page
        create_author_button = self.selenium.find_element(By.XPATH, "//a[contains(@href,'/catalog/author/create')]")
        create_author_button.click()
        
        # Fill form
        first_name_field = self.selenium.find_element(By.NAME, 'first_name')
        last_name_field = self.selenium.find_element(By.NAME, 'last_name')
        date_of_birth_field = self.selenium.find_element(By.NAME, 'date_of_birth')

        first_name_field.send_keys('Nora')
        last_name_field.send_keys('Roberts')
        date_of_birth_field.send_keys('10/10/1950')

        submit_button = self.selenium.find_element(By.XPATH, "//input[@type='submit']")

        submit_button.click()

        # Go to "Create book" page
        create_book_button = self.selenium.find_element(By.XPATH, "//a[contains(@href,'/catalog/book/create')]")
        create_book_button.click()

        # Fill form
        title_field = self.selenium.find_element(By.NAME, 'title')
        author_field = self.selenium.find_element(By.NAME, 'author')
        author_select = Select(author_field)
        isbn_field = self.selenium.find_element(By.NAME, 'isbn')
        genre_field = self.selenium.find_element(By.NAME, 'genre')
        genre_select = Select(genre_field)

        title_field.send_keys('O Despertar')
        author_select.select_by_visible_text('Roberts, Nora')
        isbn_field.send_keys('9781250272614')
        genre_select.select_by_visible_text('Fantasia Paranormal')
        genre_select.select_by_visible_text('Romance')

        submit_button = self.selenium.find_element(By.XPATH, "//input[@type='submit']")

        submit_button.click()

        # Asserts
        title = self.selenium.find_element(By.TAG_NAME, 'h1').text
        self.assertIn('O Despertar', title)

        p_tags = self.selenium.find_elements(By.TAG_NAME, "p")
        self.assertEqual(len(p_tags), 4)
        
        expected_contents = [
            "Autor: Roberts, Nora",
            "Resumo:",
            "ISBN: 9781250272614",
            "Gênero: Fantasia Paranormal, Romance"
        ]
        
        for p_tag, expected_content in zip(p_tags, expected_contents):
            self.assertIn(expected_content, p_tag.text)

        copias = self.selenium.find_element(By.TAG_NAME, 'h4').text
        self.assertIn('Cópias', copias)
