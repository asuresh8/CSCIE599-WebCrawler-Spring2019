"""
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys

class MySeleniumTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_login(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/main_app/login'))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('admin')
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('secretpass!')
        self.selenium.find_element_by_class_name('btn-success').click()

    def test_create_new_job(self):
        selenium = self.selenium
        #Opening the new_job link
        self.selenium.get('%s%s' % (self.live_server_url, '/main_app/new_job'))
        #find the form element
        name = selenium.find_element_by_id('id_name')
        type = selenium.find_element_by_id('id_type')
        domain = selenium.find_element_by_id('id_domain')
        urls = selenium.find_element_by_id('id_urls')
        description = selenium.find_element_by_id('id_description')
        docs_all = selenium.find_element_by_id('id_docs_all')
        docs_html = selenium.find_element_by_id('id_docs_html')
        docs_docx = selenium.find_element_by_id('id_docs_docx')
        docs_pdf = selenium.find_element_by_id('id_docs_pdf')
        docs_xml = selenium.find_element_by_id('id_docs_xml')
        docs_txt = selenium.find_element_by_id('id_docs_txt')
        s3_location = selenium.find_element_by_id('id_s3_location')
        num_crawlers = selenium.find_element_by_id('id_num_crawlers')
        submit = selenium.find_element_by_name('new-job-submit')

        #Fill the form with data
        name.send_keys('my_new_job_test1')
        type.send_keys('1')
        domain.send_keys('http://www.wikipedia.org')
        urls.send_keys('/test1/a\n/test2/b')
        description.send_keys('this is a test crawl')
        docs_all.send_keys('1')
        docs_html.send_keys('1')
        docs_docx.send_keys('0')
        docs_pdf.send_keys('1')
        docs_xml.send_keys('0')
        docs_txt.send_keys('0')
        s3_location.send_keys('https://mys3.amazon.com')
        num_crawlers.send_keys('2')

        #submitting the form
        submit.send_keys(Keys.RETURN)

        #check the returned result
        assert 'Check your email' in selenium.page_source
"""
