import requests
import unittest
 
import helpers
 
class TestCrawlerHelpers(unittest.TestCase):
    """
    Test the add function from the mymath library
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def test_get_links(self):
        html = """
            <HTML>
                <HEAD>
                    <TITLE>Your Title Here</TITLE>
                </HEAD>
                <BODY BGCOLOR="FFFFFF">
                    <H1>This is a Header</H1>
                    <a href="http://somegreatsite.com">This is a link</a>
                    Send me mail at <a href="mailto:support@yourcompany.com">support@yourcompany.com</a>.
                    <P> This is a new paragraph!
                </BODY>
            </HTML>"""
        mock_response = requests.models.Response()
        mock_response._content = html.encode()
        links = helpers.get_links(mock_response)
        self.assertEqual(len(links), 1)
        self.assertTrue('http://somegreatsite.com' in links)

 
if __name__ == '__main__':
    unittest.main()