import json

baike_path = 'spider_results/results.json'
cnki_path = './input/cnki.json'
cooperation_path = 'cooperation_analyse/output/output.json'

def load_data(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def cnki_extension(path):
    data = load_data(path)
    for type_ in ["Author-作者", "Organ-单位", "Keyword-关键词", "Keyword_of_abstract"]:
        info_extension(data,type_)
    source_extention(data)

def info_extension(data,type_):
    gotten = []
    urls = {}
    for item in (item for info in data.values() for item in info.get(type_, [])):
        if item in gotten:
            continue
        gotten.append(item)
        url = f'https://baike.baidu.com/item/{item}?fromModule=lemma_search-box'
        urls[item] = url
    save_json(urls, type_)
    print(f"{type_} Finished!")

def source_extention(data):
    gotten = []
    urls = {}
    for source in (info.get('Source-文献来源', 'unknown') for info in data.values()):
        if source in gotten:
            continue
        gotten.append(source)
        url = f'https://baike.baidu.com/item/{source}?fromModule=lemma_search-box'
        urls[source] = url
        save_json(urls, 'Source-文献来源')
    print("Source-文献来源 Finished!")

def save_json(data, type_):
    with open(f'./output/{type_}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

if __name__ == '__main__':
    cnki_extension(path=cnki_path)
    print("Finished!")

