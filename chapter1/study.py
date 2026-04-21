import re

text = "我的代码在 Cursor 中运行，效率很高。"
pattern = r"Cursor"

match = re.search(pattern, text)

if match:
    print(f"找到了关键词: {match.group()}")
    print(f"出现的位置范围: {match.span()}")
else:
    print("未找到匹配项")
