import json

#写入json数据文件（obj->json）
# 字典对象
user = {
    "name": "Tom",
    "age": 22,
    "hobby": [
        "reading",
        "playing"
    ]
}

# 对象序列化为json
"""
with open("resources/user.json", "w", encoding="utf-8") as file1:
    # ensure_ascii=False：支持中文。indent=2：缩进2个空格
    json.dump(user, file1, ensure_ascii=False, indent=2)
"""

# 读取json数据文件（json->obj）
with open("resources/user.json", "r", encoding="utf-8") as file2:
    userobj = json.load(file2)
    print(type(userobj))




