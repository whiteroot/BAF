import unittest

from utils import getMillionList, KILO, MEGA, isAccount


class TestUtils(unittest.TestCase):

    def setUp(self):
        pass

    def testMillionsGen(self):
        self.doTest(10, 99, KILO)
        self.doTest(100, 999, KILO)
        self.doTest(1, 9, MEGA)
        self.doTest(10, 99, MEGA)
        self.doTest(100, 999, MEGA)

    def doTest(self, i, j, prefix):
        x = getMillionList(i, j, prefix)
        print(f"i={i}   j={j}   prefix={prefix}")
        if len(x) > 33:
            print(x[:32])
        else:
            print(x)
        assert(x[0] == (i, 0, prefix))
        if prefix == KILO:
            assert(x[-1] == (j, 0, prefix))
        else:
            assert(x[-1] == (j, 9, prefix))
            assert( (i, 2, prefix) in x)
            assert( (j-1, 5, prefix) in x)

    def testIsAccount(self):
        self.assertTrue(isAccount('https://www.instagram.com/bob/'))
        self.assertTrue(isAccount('https://www.instagram.com/bob/?hl=fr'))
        self.assertTrue(isAccount('https://www.instagram.com/bob'))
        self.assertFalse(isAccount('https://www.instagram.com/bob/p/'))
        self.assertFalse(isAccount('https://www.instagram.com/'))
        self.assertFalse(isAccount('https://www.instagram.com'))


