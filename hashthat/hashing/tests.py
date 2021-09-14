from django.core.exceptions import ValidationError
from django.test import TestCase
import hashlib
import time

from selenium import webdriver

from .forms import HashForm
from .models import Hash

LOWERCASE_HELLO_HASH = '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824'
UNKNOWN_HASH = '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'

class FunctionalTestCase(TestCase):

    def setUp(self):
        self.browser = webdriver.Chrome()

    def _get_homepage(self):
        self.browser.get('http://localhost:8000')

    def _type_hello(self):
        textbox = self.browser.find_element_by_id('id_text')
        textbox.send_keys('hello')

    def test_there_is_homepage(self):
        self._get_homepage()
        self.assertIn('Enter hash here:', self.browser.page_source)

    def test_hash_of_hello(self):
        self._get_homepage()
        self._type_hello()
        self.browser.find_element_by_name('submit').click()
        self.assertIn(
            '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824', self.browser.page_source)

    def test_hash_ajax(self):
        self._get_homepage()
        self._type_hello()
        time.sleep(5)  # wait for AJAX
        self.assertIn(LOWERCASE_HELLO_HASH, self.browser.page_source)

    def tearDown(self):
        self.browser.quit()


class UnitTestCase(TestCase):

    def setUp(self):
        pass

    def test_home_homepage_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'hashing/home.html')

    def test_hash_form(self):
        form = HashForm(data={'text': 'hello'})
        self.assertTrue(form.is_valid())

    def test_hash_func_works(self):
        text_hash = hashlib.sha256('hello'.encode('utf-8')).hexdigest()
        self.assertEqual(LOWERCASE_HELLO_HASH, text_hash)

    def _create_hello_hash(self):
        hashobj = Hash()
        hashobj.text = 'hello'
        hashobj.hash = LOWERCASE_HELLO_HASH
        hashobj.save()
        return hashobj

    def test_hash_object(self):
        hashobj = self._create_hello_hash()
        pulled_hash = Hash.objects.get(hash=LOWERCASE_HELLO_HASH)
        self.assertEqual(hashobj.text, pulled_hash.text)

    def test_viewing_hash(self):
        self._create_hello_hash()
        response = self.client.get(f'/hash/{LOWERCASE_HELLO_HASH}')
        self.assertContains(response, 'hello')

    def test_404_on_unknown_hash(self):
        response = self.client.get(f'/hash/{UNKNOWN_HASH}')
        self.assertEqual(response.status_code, 404)

    def test_bad_data(self):
        def bad_hash():
            hashobj = Hash()
            hashobj.hash = UNKNOWN_HASH + 'ggggg'
            hashobj.full_clean()
        self.assertRaises(ValidationError, bad_hash)
        
    def tearDown(self):
        pass

