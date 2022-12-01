'''去重'''

import json

with open('./spider_results/urls.json', 'r', encoding='utf-8') as f:
    urls:dict[str, dict[str, str]] = json.load(f)

result = {}
for item in urls.values():
    result.update(item)

with open('./spider_results/related_things.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False)

print("Finished!")