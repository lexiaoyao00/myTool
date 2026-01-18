import re

texts = [
    "N0780",
    "PONDO-011526_001",
    "MIDE-565-C",
    "031523-001",
    "avav77.xyz@MIDE565",
    "abCD123xyz",
    "avav77.xyz@031523-001-carib",
    "MIDE-565-C",
    "(Caribbean)(040415-846)ストリップ劇場まな板本番ショー 波多野結衣",
    "PONDO-011526_001",
    'fc2-ppv-4831115',
]

# 1. 先替换所有下划线为短横
def normalize(text):
    return text.replace("_", "-")

# 2. 正则匹配: 至少一个字母或数字，可选短横分隔部分
# pattern = re.compile(r'\b[0-9A-Za-z]+(?:-[0-9A-Za-z]+)*\b')
pattern = re.compile(r'\b[0-9A-Za-z]+(?:-[0-9A-Za-z]+)*\d\b')

for t in texts:
    norm_t = normalize(t)
    matches = pattern.findall(norm_t)
    if matches:
        print(f"{t} → {matches}")
    else:
        print(f"{t} → 未匹配")
