import unittest

class TestMain(unittest.TestCase):

    def testMain(self):
        self.assertTrue(True)


def main():
    return unittest.main()

if __name__ == '__main__':
    main()