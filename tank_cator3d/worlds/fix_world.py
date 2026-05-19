import re
with open('bookstore.world', 'r', encoding='utf-8') as f:
    data = f.read()
pattern = re.compile(r'<model name="([^"]+)">[\s\S]*?<uri>([^<]+)</uri>[\s\S]*?<pose[^>]*>([^<]+)</pose>[\s\S]*?</model>')
out = pattern.sub(r'<include>\n    <name>\1</name>\n    <uri>\2</uri>\n    <pose>\3</pose>\n</include>', data)
with open('bookstore.world', 'w', encoding='utf-8') as f:
    f.write(out)
print("Đã sửa cấu trúc file bookstore.world thành công!")
