import  json

def load_data(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyse_data(data: dict[str, dict[str, str | list]]):
    # {author: [(article, authors)])}
    result = {}
    for article, info in data.items():
        for author in info.get('Author-作者', []):
            authors = info['Author-作者'][::]
            authors.remove(author)
            result[author] = result.get(author, [])+[(article, authors)]
    f = open('./output/output.json', 'w', encoding='utf-8')
    json.dump(result, f, ensure_ascii=False)
    f.close()

if __name__ == '__main__':
    path = './input/cnki.json'
    data = load_data(path)
    analyse_data(data)
    print("Finished!")
