import logging
import unittest
 
import crawler_context
 
class TestCrawlerContext(unittest.TestCase):
    """
    Test the add function from the mymath library
    """

    def setUp(self):
        self.context = crawler_context.Context(logging.getLogger())

    def tearDown(self):
        pass
    
    # TODO: delete this noop test and write actual unit tests
    def test_context_thread_count_functionality(self):
        self.assertEqual(self.context.active_thread_count.get(), 0)
        self.context.active_thread_count.increment()
        self.assertEqual(self.context.active_thread_count.get(), 1)
        self.context.active_thread_count.decrement()
        self.assertEqual(self.context.active_thread_count.get(), 0)
 
 
if __name__ == '__main__':
    unittest.main()