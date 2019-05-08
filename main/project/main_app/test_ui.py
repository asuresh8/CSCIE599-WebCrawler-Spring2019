from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from unittest.mock import Mock, patch
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.contrib.auth.models import User

class MySeleniumTests(StaticLiveServerTestCase):

    def setUp(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--window-size=1420,1080')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        self.selenium = webdriver.Chrome(chrome_options=chrome_options)
        super(MySeleniumTests, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(MySeleniumTests, self).tearDown()
    
    def test_create_new_job(self):
        """
        Tests creating a new crawl job using Selenium driver.
        """
        user = User.objects.create_user('testNewJob', 'testNewJob@random42524482827.com', 'testpassword')
        self.selenium.get('%s%s' % (self.live_server_url, '/main_app/login'))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('testNewJob')
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('testpassword')
        self.selenium.find_element_by_class_name('btn-success').click()

        #Opening the new_job link
        self.selenium.get('%s%s' % (self.live_server_url, '/main_app/new_job'))
        #find the form element
        name = self.selenium.find_element_by_id('id_name')
        type = self.selenium.find_element_by_id('id_type')
        domain = self.selenium.find_element_by_id('id_domain')
        urls = self.selenium.find_element_by_id('id_urls')
        description = self.selenium.find_element_by_id('id_description')
        docs_all = self.selenium.find_element_by_id('id_docs_all')
        docs_html = self.selenium.find_element_by_id('id_docs_html')
        docs_docx = self.selenium.find_element_by_id('id_docs_docx')
        docs_pdf = self.selenium.find_element_by_id('id_docs_pdf')
        num_crawlers = self.selenium.find_element_by_id('id_num_crawlers')
        sub = self.selenium.find_element_by_id('new-job-submit')

        #Fill the form with data
        name.send_keys('my_new_job_test1')
        type.send_keys('1')
        domain.send_keys('http://www.wikipedia.org')
        urls.send_keys('/test1/a;/test2/b')
        description.send_keys('this is a test crawl')
        docs_all.send_keys('1')

        docs_html.send_keys('1')
        docs_docx.send_keys('0')
        docs_pdf.send_keys('1')
        num_crawlers.send_keys('2')


        #submitting the form
        with patch('main_app.views.launch_crawler_manager') as mock_launch:
            sub.send_keys(Keys.RETURN)

        #check the returned result
        #assert 'Check your email' in selenium.page_source

    def test_login(self):
        """
         Tests login functionality using Selenium driver.
         """
        user = User.objects.create_user('testUi', 'testUi@random42524482827.com', 'testpassword')
        self.selenium.get('%s%s' % (self.live_server_url, '/main_app/login'))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('testUi')
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('testpassword')
        self.selenium.find_element_by_class_name('btn-success').click()
