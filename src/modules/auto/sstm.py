import curl_cffi
from parsel import Selector
# from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
from datetime import datetime
import asyncio
import time

class SSTM:
    def __init__(self):
        self.init()

    def init(self):
        self.cookies = {
            'ips4_forum_view': 'table',
            'ips4_forum_list_view': 'list',
            'ips4_device_key': 'ec8436fed13d9a722cf5d9497a5f0a92',
            'ips4_member_id': '321994',
            'ips4_login_key': '7a6a53672e5f06febbfa9c55bf785f33',
            'ips4_ss_id': 'fc4a33a463bd450be0b8f7f343d238ad',
            'ips4_IPSSessionFront': 'vp1gl2jb2jvsk1lcbncrb1kr2o',
            'ips4_loggedIn': '1759899832',
            'ips4_ipsTimezone': 'Asia/Shanghai',
            'ips4_hasJS': 'true',
        }

        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,en-US;q=0.6',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'referer': 'https://sstm.moe/?_fromLogin=1',
            'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        }
        self.session = curl_cffi.Session()

    def checkInLink(self):

        response = self.session.get('https://sstm.moe/forum/72-%E5%90%8C%E7%9B%9F%E7%AD%BE%E5%88%B0%E5%8C%BA/', headers=self.headers, cookies=self.cookies)

        # print(response.text)
        sel = Selector(text=response.text)

        link = sel.css('.cForumTopicTable.cTopicList  > li:nth-child(1) > div.ipsDataItem_icon.ipsPos_top > a::attr(href)').get()

        return link

    async def autoCheckIn(self,checkInLink:str,email:str,passwd:str):
        if checkInLink is None:
            print('空链接')
            return

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                extra_http_headers=self.headers
            )
            # context.add_cookies([self.cookies])

            page = await context.new_page()
            await page.goto(checkInLink)

            await page.locator('a#elUserSignIn').click()
            await page.locator('ul.ipsList_reset input[type="email"]').fill(email)
            await page.locator('ul.ipsList_reset input[type="password"]').fill(passwd)
            await page.locator('ul.ipsList_reset button[type="submit"]').click()

            # editor = page.wait_for_selector('div[data-role="editorComposer"] input',timeout=5000)
            # if editor is None:
            #     page.locator('div[data-role="editorComposer"] div.ipsComposeArea_dummy.ipsJS_show').click()
            time.sleep(1)
            # editorComposer = await page.wait_for_selector('div[data-role="editorComposer"] div.ipsComposeArea_dummy.ipsJS_show')
            # editorComposer = await page.wait_for_selector('a.ipsButton.ipsButton_important.ipsButton_medium.ipsButton_fullWidth[rel="nofollow"]')
            # page.locator('div[data-role="editorComposer"] div.ipsComposeArea_dummy.ipsJS_show').click()
            # await editorComposer.click()
# style="display: none;"

            editorComposer = page.locator("#comments").get_by_text("回复此主题")
            await editorComposer.scroll_into_view_if_needed()
            await editorComposer.click()
            for i in range(10):
                editorStyle =  await editorComposer.get_attribute('style')
                if editorStyle is not None:
                    break

                print(f'答复位置未找到，重复点击尝试 {i+1}')
                await editorComposer.scroll_into_view_if_needed()
                await editorComposer.click()
                time.sleep(2)


            editor = page.locator('div[data-role="editorComposer"] div.cke_inner  div#cke_1_contents div.cke_wysiwyg_div')

            # editor = await page.wait_for_selector('div[data-role="editorComposer"] div.cke_inner  div#cke_1_contents div.cke_wysiwyg_div')
            # editor = page.locator('div[data-role="editorComposer"] input[type="hidden"]')
            # editor = page.wait_for_selector('div[data-role="editorComposer"] input[type="hidden"]')

            if editor is not None:
                # await page.pause()
                print('签到位置找到，尝试填写内容并提交')
                content =  datetime.now().strftime('%Y-%m-%d')
                await editor.fill(content)
                await page.locator('ul.ipsToolList li button[type="submit"]').click()
            else:
                print('签到位置未找到')

            await browser.close()



def testSSTM():
    sstm = SSTM()
    # print(sstm.checkInLink())
    link = sstm.checkInLink()
    print('登录链接：')
    print(link)

    email = '2950848462@qq.com'
    passwd = 'xc1290435868+'

    asyncio.run(sstm.autoCheckIn(checkInLink=link,email=email,passwd=passwd))




if __name__ == '__main__':
    testSSTM()


