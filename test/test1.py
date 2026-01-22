

def test():
    try:
        for i in range(10):
            print(i)
            if i == 5:
                return
    except Exception as e:
        print(e)
    finally:
        print("finally")


def test2():
    with open('e:\\GIT_pros\\myTool\\storage\\data\\hanime\\nfo\\OVA サキュバス喚んだら義母が来た!\\召喚魅魔結果義母來了!  1.nfo', 'w') as f:
        f.write('test')


if __name__ == '__main__':
    test2()

