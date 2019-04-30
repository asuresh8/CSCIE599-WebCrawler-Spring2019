import unittest
 
import atomic
 
class TestCrawlerManagerAtomic(unittest.TestCase):
    """
    Test the add function from the mymath library
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    # TODO: delete this noop test and write actual unit tests
    def test_queue(self):
        queue = atomic.AtomicQueue()
        queue.add('1')
        queue.add('2')
        self.assertTrue(queue.contains('1'))
        self.assertTrue(queue.contains('2'))
        self.assertEqual(queue.size(), 2)
        self.assertEqual(queue.poll(), '1')
        self.assertEqual(queue.size(), 1)
        self.assertEqual(queue.poll(), '2')
        self.assertEqual(queue.size(), 0)
    
    def test_priority_queue(self):
        queue = atomic.AtomicPriorityQueue()
        queue.add('www.recurship.com', len('www.recurship.com'))
        queue.add('www.google.com', len('www.google.com'))
        self.assertTrue(queue.contains('www.google.com'))
        self.assertTrue(queue.contains('www.recurship.com'))
        self.assertEqual(queue.size(), 2)
        self.assertEqual(queue.poll(), (len('www.google.com'), 'www.google.com'))
        self.assertEqual(queue.size(), 1)
        self.assertEqual(queue.poll(), (len('www.recurship.com'), 'www.recurship.com'))
        self.assertEqual(queue.size(), 0)
        self.assertEqual(queue.poll(), (None, None))

    def test_set(self):
        my_set = atomic.AtomicSet()
        my_set.add('1')
        my_set.add('2')
        self.assertTrue(my_set.contains('1'))
        self.assertTrue(my_set.contains('2'))
        my_set.remove('1')
        my_set.remove('2')
        self.assertFalse(my_set.contains('1'))
        self.assertFalse(my_set.contains('2'))
    
    def test_counter(self):
        counter = atomic.AtomicCounter()
        self.assertEqual(counter.get(), 0)
        counter.increment()
        self.assertEqual(counter.get(), 1)
        counter.increment()
        counter.increment()
        self.assertEqual(counter.get(), 3)

 
if __name__ == '__main__':
    unittest.main()