import unittest
 
import atomic
 
class TestCrawlerAtomic(unittest.TestCase):
    """
    Test the add function from the mymath library
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    # TODO: delete this noop test and write actual unit tests
    def test_counter(self):
        counter = atomic.AtomicCounter()
        self.assertEqual(counter.get(), 0)
        counter.increment()
        self.assertEqual(counter.get(), 1)
        counter.increment()
        counter.increment()
        self.assertEqual(counter.get(), 3)
        counter.decrement()
        self.assertEqual(counter.get(), 2)
 
 
if __name__ == '__main__':
    unittest.main()