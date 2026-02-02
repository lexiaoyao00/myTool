import curl_cffi

cookies = {
    # 'remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d': 'eyJpdiI6IlwvUG91V2NmNTRuSXl2NEtKek9aQ0F3PT0iLCJ2YWx1ZSI6Iks4R3FUekdCVHZwVjREYnkrUUFYY2NyNm9iaUszditPOGp5ME1OTm16WTJXSTRLekNkVEU0bkM1aDlmbXlLOGsrOEthRUYzY1A2bmp0OTFYeEsxM2lCMTl6VGh0NThuZnRvUzFXK2hjSlQ1eTFRYllmVzgxTU5pK1E4OGx3cE1CRmZIekFzVnZvY0VCZzJmNFRZb041U3BoU0poNHZuWm5qeEpNUDhMTDdFQllFakg0MDV5Y0xQXC84TjM3SEgzeHkiLCJtYWMiOiJjMzY0YWE0NzhmNWZkOTRhYjYwYzc0NzBhYzUwYmRjMWQ1YjQ0ZWNhOWQ2YjQzMWU5Mjg3YWNiZjExZjRkMWVkIn0%3D',
    'user_lang': 'zhs',
    '_gid': 'GA1.2.1049050028.1770000345',
    # 'fpestid': '1fidryrSRR9IouoTi3iCMGJQAd2PYJ_uXj1DYr3FcIm1-n-p1LwKt2PVar1HU6eCJy10cw',
    '_ga_2JNTSFQYRQ': 'GS2.1.s1770000343$o43$g1$t1770003100$j60$l0$h0',
    # 'XSRF-TOKEN': 'eyJpdiI6IkJWRXA4UVFEaGZCZzRSZlZSWm5uaFE9PSIsInZhbHVlIjoicmMrRWVVTUptMHFSOTdMN0ZVMkNEenZ6YkdBZVhua1VuckRWbm5OWlpaMERSSHBqUHFVRTlXQnJCcjhcL1NNRlwvIiwibWFjIjoiNTI3ODllMWEzODI2ZmFiY2MyNjI3Nzk5NjRmOWExODFhODVjMzI0NDkyMjBhNzI5ZjdhZDZjZTYyMjlkNWY1YSJ9',
    # 'hanime1_session': 'eyJpdiI6Ik1Dd1dhejVDSjNCMVZLVUdcL3BPUm1nPT0iLCJ2YWx1ZSI6Im90bklvR2xHNFVhSTJtYlwvOE81K0JFUnY0S0p5NmxsT2tlMGNzaU5oMG1mWkJkZFBrYnc0RWw1M0RUNmF4QUlJIiwibWFjIjoiNDVjZTQzNDAwYTlhMjY2M2EzOTY5MTE0MTJkM2FjYmMwNDk4ZjU1ZjBiNDFjNWU1ZTE2MWQ2NmZlYWI5YzJkNSJ9',
    '_ga': 'GA1.2.120883284.1751720600',
    '_gat_gtag_UA_125786247_2': '1',
    'cf_clearance': 'OqpuY7nwvCQ2XOVv2q6GjNdlb_t8w3LV0r0JwB1o_sc-1770003369-1.2.1.1-1yHQtR20mC2nx.PLybwRzqtDoKjbyCtmtg.t5a885mZGw4dSS1QmEZx8ukpu3Vbci7VyubLu.vCHhNipwyz8R5XTgm0EjoBhz8p8WK_qduAknWrKy7acvA1dlqF5vqmBkEr.hNomRIYVgisvJRdn7qU6p_eWGafGNu1Bn1vFTjsJtYISEUZCTN2FkFF80eFvZKNchvP8lGbPVRLYsl9cmF5SstsU03VTxoGAD_SVmVaer.tr1o2UUEXSYwlb3EFT',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,en-US;q=0.6',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'referer': 'https://hanime1.me',
    'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    'sec-ch-ua-arch': '"x86"',
    'sec-ch-ua-bitness': '"64"',
    'sec-ch-ua-full-version': '"144.0.7559.110"',
    'sec-ch-ua-full-version-list': '"Not(A:Brand";v="8.0.0.0", "Chromium";v="144.0.7559.110", "Google Chrome";v="144.0.7559.110"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua-platform-version': '"10.0.0"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
}

params = (
    ('v', '87075'),
)

response = curl_cffi.get('https://hanime1.me/watch', headers=headers, params=params, cookies=cookies,impersonate='chrome142')

#NB. Original query string below. It seems impossible to parse and
#reproduce query strings 100% accurately so the one below is given
#in case the reproduced version is not "correct".
# response = requests.get('https://hanime1.me/watch?v=87075', headers=headers, cookies=cookies)

print(response.status_code)
with open('test1.html', 'w', encoding='utf-8') as f:
    f.write(response.text)

