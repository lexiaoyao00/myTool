

from typing import Union, Dict, List
import curl_cffi
# from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
from pathlib import Path
import cv2
import numpy as np
import ddddocr

import asyncio

async def test_laowang():

    cookies = {
        '_ga': 'GA1.1.767626091.1749998724',
        'X9wU_2132_smile': '1D1',
        'X9wU_2132_visitedfid': '65D47D45',
        'X9wU_2132_saltkey': 'H12h25Xu',
        'X9wU_2132_lastvisit': '1762582201',
        'X9wU_2132_auth': '16e4TJteK5qBIHAuon0aFtEJJqCpcQUZlibcGjuxbrbJyLS4MUjA3kfPMWw5DvqeIrTE%2FaayQLB15%2B5LWsoZhrwF0plm',
        'X9wU_2132_lastcheckfeed': '2647033%7C1762585832',
        'X9wU_2132_ulastactivity': '1762670186%7C0',
        'cf_clearance': 'EPGsWFONw.yVbtAYdEN8lbzZ9Tp4fiNFj47YhkYl.VU-1762670187-1.2.1.1-f3QriHbSsOyVlQsPimSwH7f8GG6SFBJADiW.OlNYvxhjCzMRvFNcj2qC4o6LzKFwoCFghXHQZpQ.Op1pG2nO79J1Wjc6PJ1hTaJFHyTkhumE8EMGClPnr.2yA5jetBneTsZwKsyg0i4KbFqVQfw16frlNIjpWKZA3CZJAcMPUP.dWWXWawTlgs3.WQ.UsmY0f3do0K_dxur0Sk3FFO7rzqp2.5BDEsVBBUQj9v8Wa3s',
        'PHPSESSID': '4i1spmv55qtinbvvf237q08pg5',
        '_ga_BGYP9PD1HB': 'GS2.1.s1762670808$o21$g0$t1762670808$j60$l0$h0',
        'X9wU_2132_lastact': '1762670808%09plugin.php%09',
    }

    playwright_cookies = curl_cffi_cookies_to_playwright(cookies, 'laowang.vip')

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        await context.add_cookies(playwright_cookies)
        page = await context.new_page()
        await page.goto('https://laowang.vip/plugin.php?id=k_misign:sign')

        # cookies = page.context.cookies()

        # print(cookies)

        await page.locator('a.btn.J_chkitot').click()

        await page.wait_for_timeout(1000)
        # with page.expect_request("https://laowang.vip/captcha/tncode.php*") as first:
        #     print(first.value.url)
        # with page.expect_request("**/captcha/tncode**") as first:
        #     print(first.value.url)
        async with page.expect_request("**/captcha/tncode.php*") as first:
            await page.locator('div#tncode').click()

        # print(first.value.url)
        request = await first.value
        response = await request.response()
        response_content = await response.body()
        path = Path('tmp/tncode.png')
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(str(path), "wb") as f:
            f.write(response_content)

        offset = int(getOffset(str(path)))
        print(offset)
        await page.wait_for_timeout(1000)

        slide = page.locator('div.slide div.slide_block')
        slide_box = await slide.bounding_box()
        start_x = slide_box['x'] + slide_box['width'] / 2
        start_y = slide_box['y'] + slide_box['height'] / 2

        # 按下鼠标拖拽
        await page.mouse.move(start_x, start_y)
        await page.mouse.down()
        # page.mouse.move(start_x + offset, start_y, steps=10)
        steps = 10
        for i in range(steps + 1):
            progress = ease_out_quad(i / steps)
            current_x = start_x + offset * progress
            await page.mouse.move(current_x, start_y)
            await page.wait_for_timeout(20)

        await page.mouse.up()


        # page.pause()

        # 提交
        await page.wait_for_timeout(1000)
        await page.locator('form div.button-row button#submit-btn').click()

        await browser.close()


def curl_cffi_cookies_to_playwright(curl_cookies: Dict[str, str], domain: str) -> List[Dict]:
    """
    将 curl_cffi 的 cookies 转换为 Playwright 可用的 cookies 列表

    :param curl_cffi_cookies: curl_cffi 的 cookies (可以是 client.cookies 或简单字典)
    :param domain: 目标域名，比如 "example.com"
    :return: Playwright cookies 列表
    """
    result = []

    # 如果传的是 Cookies 对象 (类似 requests.cookies.RequestsCookieJar)
    # if hasattr(curl_cffi_cookies, "items"):
    #     iterable = curl_cffi_cookies.items()
    # elif isinstance(curl_cffi_cookies, dict):
    #     iterable = curl_cffi_cookies.items()
    # else:
    #     raise TypeError("Unsupported cookies type, must be dict or curl_cffi Cookies.")

    iterable = curl_cookies.items()

    for name, value in iterable:
        cookie_obj = {
            "name": name,
            "value": value,
            "domain": domain,
            "path": "/",
            "httpOnly": False,
            "secure": False,
            "sameSite": "Lax",
        }
        result.append(cookie_obj)

    return result

def getOffset(path: str):
    img = cv2.imread(path)
    # 获取图像尺寸
    height, width, channels = img.shape

    # 每份的高度
    part_height = height // 3

    # 逐份切割
    img1 = img[0:part_height, 0:width]              # 第一份（顶部）
    img2 = img[part_height:part_height*2, 0:width]  # 第二份（中间）
    img3 = img[part_height*2:height, 0:width]       # 第三份（底部）

    # 保存切割结果
    cv2.imwrite('tmp/bg.jpg', img1)
    cv2.imwrite('tmp/slider.jpg', img2)
    cv2.imwrite('tmp/full.jpg', img3)

    print("切割完成")
    slide('tmp/slider.jpg')
    print("主体提取完成")
    return ocr('tmp/output_cropped.png', 'tmp/bg.jpg')

def slide(slider_path: str = 'tmp/slider.jpg'):
    # 读取图片
    img = cv2.imread(slider_path)

    # 转为 RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # 创建掩码（非黑色部分）
    lower = np.array([0, 0, 0])
    upper = np.array([40, 40, 40])  # 黑色的范围，可调
    mask = cv2.inRange(img_rgb, lower, upper)
    mask_inv = cv2.bitwise_not(mask)  # 保留非黑色

    # 找到非黑色区域的列范围
    coords = cv2.findNonZero(mask_inv)  # 所有非黑色的坐标点
    x, y, w, h = cv2.boundingRect(coords)  # 返回最小边界框

    # 裁剪宽度，但保持原图高度
    cropped_img = img[:, x:x+w]  # 按列裁剪

    # 分离通道并加 alpha
    b, g, r = cv2.split(cropped_img)
    alpha = mask_inv[:, x:x+w]
    rgba = cv2.merge([b, g, r, alpha])

    Path(slider_path).unlink()

    # 保存结果
    save_path = 'tmp/output_cropped.png'
    cv2.imwrite(save_path, rgba)

    print(f"主体提取并裁剪完成，{save_path}")


def ease_out_quad(t):
    return 1 - (1 - t) * (1 - t)

def ocr(slider_path:str,bg_path:str):
    slide = ddddocr.DdddOcr(det=False,ocr=False,show_ad=False)

    with open(slider_path, 'rb') as f:
        slide_bytes = f.read()

    with open(bg_path, 'rb') as f:
        bg_bytes = f.read()

    res = slide.slide_match(slide_bytes, bg_bytes)

    # print(res)
    return res['target'][0]

def test_request():

    cookies = {
        '_ga': 'GA1.1.767626091.1749998724',
        'X9wU_2132_smile': '1D1',
        'X9wU_2132_visitedfid': '65D47D45',
        'X9wU_2132_saltkey': 'H12h25Xu',
        'X9wU_2132_lastvisit': '1762582201',
        'X9wU_2132_auth': '16e4TJteK5qBIHAuon0aFtEJJqCpcQUZlibcGjuxbrbJyLS4MUjA3kfPMWw5DvqeIrTE%2FaayQLB15%2B5LWsoZhrwF0plm',
        'X9wU_2132_lastcheckfeed': '2647033%7C1762585832',
        'X9wU_2132_ulastactivity': '1762670186%7C0',
        'cf_clearance': 'EPGsWFONw.yVbtAYdEN8lbzZ9Tp4fiNFj47YhkYl.VU-1762670187-1.2.1.1-f3QriHbSsOyVlQsPimSwH7f8GG6SFBJADiW.OlNYvxhjCzMRvFNcj2qC4o6LzKFwoCFghXHQZpQ.Op1pG2nO79J1Wjc6PJ1hTaJFHyTkhumE8EMGClPnr.2yA5jetBneTsZwKsyg0i4KbFqVQfw16frlNIjpWKZA3CZJAcMPUP.dWWXWawTlgs3.WQ.UsmY0f3do0K_dxur0Sk3FFO7rzqp2.5BDEsVBBUQj9v8Wa3s',
        'PHPSESSID': '4i1spmv55qtinbvvf237q08pg5',
        '_ga_BGYP9PD1HB': 'GS2.1.s1762670808$o21$g0$t1762670808$j60$l0$h0',
        'X9wU_2132_lastact': '1762670808%09plugin.php%09',
    }

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,en-US;q=0.6',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'referer': 'https://laowang.vip/forum.php',
        'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
    }

    params = (
        ('id', 'k_misign:sign'),
    )

    session = curl_cffi.Session()

    response = session.get('https://laowang.vip/plugin.php', headers=headers, params=params, cookies=cookies,impersonate='chrome110')

    print(session.cookies)
    # print(response.text)
    with open('laowang.html', 'w', encoding='utf-8') as f:
        f.write(response.text)

if __name__ == '__main__':
    asyncio.run(test_laowang())
    # test_request()