import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET


# cbz_path = 'manga/(C99) [でんしこ！ (凹凸でん)] 切ちゃんの山中コンビニ露出クエスト (戦姫絶唱シンフォギア) [中国翻訳].cbz'
# xml_content = ET.parse('ComicInfo.xml')
# # print(xml_content)
# # 把 XML 插入 CBZ
# with zipfile.ZipFile(cbz_path, 'a') as zipf:
#     # 先检查是否存在旧 ComicInfo.xml
#     try:
#         zipf.getinfo("ComicInfo.xml")
#         print(f'[WARN] {cbz_path} 已存在 ComicInfo.xml，跳过')
#     except KeyError:
#         pass

#     zipf.write("ComicInfo.xml")

