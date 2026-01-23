

class Test:
    _test_dict = {}


    @staticmethod
    def test(i,s):
        str_t =  Test._test_dict.get(i)
        if not str_t:
            Test._test_dict[i] = s
            print(Test._test_dict)


if __name__ == '__main__':
    Test.test(1,'a')
    Test.test(3,'c')
    Test.test(2,'b')
    Test.test(1,'a')

