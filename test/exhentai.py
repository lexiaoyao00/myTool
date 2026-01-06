import curl_cffi

cookies = {
    'ipb_member_id': '5663118',
    'ipb_pass_hash': '926d3a8283b0beaf3fa3d22ac5580b16',
    'igneous': 'dkb9d5u5ivd4fu1o7',
    'sk': 'ot1s9e54uuvfw7sftcz2a3nowq0l',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,en-US;q=0.6',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'referer': 'https://exhentai.org',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
}

response = curl_cffi.get('https://exhentai.org/g/2798035/1156df70a5/', headers=headers, cookies=cookies)
# print(response.text)
with open('test.html', 'w') as f:
    f.write(response.text)
