import httpx
import asyncio
import re
from parsel import Selector
import os
import json


class UrlsLoader():
    def __init__(self, urls: dict[str, str], batch_size):
        self.urls = list(urls.items())
        self.batch_size = batch_size
        self.cur = 0
        self.len = len(urls)

    def __iter__(self):
        while True:
            if self.cur + self.batch_size < self.len:
                yield (self.index_urls(self.cur + i)for i in range(self.batch_size))
            else:
                yield (self.index_urls(i) for i in range(self.cur, self.len))
                break
            self.cur += self.batch_size
    
    def index_urls(self, index_num):
        return self.urls[index_num]

def first_parse(t: str):
    try:
        t = t.replace('\xa0', '')
        t = t.replace('\n', '')
    except:
        pass
    return t.strip('\n')

def second_parse(values: list):
    pattern = re.compile(r'>([\w|\s|、|（|）|.|,|，|。|、|-]+?)<')
    results = []
    for i in values:
        result = re.findall(pattern, i)
        results.append(result)
    values = [''.join(i) for i in results]
    return values


async def spider(target, url):
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url, follow_redirects=True,timeout=3)
        except:
            print(f'{target} failed time out')
            await queue_log.put({target: url})
            return
        if r.status_code != 200:
            print(f'{target} failed error response')
            await queue_log.put({target: url})
            return
        response = Selector(r.text)
        keys = response.css('dt.basicInfo-item::text').getall()
        keys = [first_parse(i) for i in keys if i != '\n']
        values = response.css('dd.basicInfo-item').getall()
        values = [first_parse(i) for i in values if i != '\n']
        values = second_parse(values)
        instruction = response.css('div.lemma-summary').getall()
        instruction = [first_parse(i) for i in instruction if i != '\n']
        instruction = second_parse(instruction)
        await queue.put({target: dict(zip(keys, values)) | {'简介': ''.join(instruction)}})
        await queue_schedule.put(target)
      

async def save_result():
    results_path = './spider_results/results.json'
    results = {}
    if os.path.exists(results_path):
        with open(results_path, 'r', encoding='utf-8') as f:
            results = json.load(f)
    while result := await queue.get():
        results |= result
        # print(results)
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False)
    print('Finished!')

async def schedule(total):
    num = 0
    while source := await queue_schedule.get():
        num += 1
        print(f'{source} finished {num}/{total}')


def load_urls():
    with open('./spider_results/related_things.json', 'r', encoding='utf-8') as f:
        return json.load(f)
    # with open('./spider_results/log.json', 'r', encoding='utf-8') as f:
    #     return json.load(f)

async def save_log():
    msgs = {}
    while msg := await queue_log.get():
        msgs |= msg
        with open('./spider_results/log.json', 'w', encoding='utf-8') as f:
            json.dump(msgs, f, ensure_ascii=False)

async def run(urls):
    batch_size = 8
    halt = 2
    urls_loader = UrlsLoader(urls, batch_size)
    for batch in urls_loader:
        await asyncio.gather(*(spider(target, url) for target, url in batch))
        await asyncio.sleep(halt)
    await queue.put(None)
    await queue_schedule.put(None)
    await queue_log.put(None)

def main():
    urls = load_urls()
    total = len(urls)
    loop = asyncio.new_event_loop()
    coros = [run(urls), save_result(), schedule(total), save_log()]
    coro = asyncio.wait(coros)
    loop.run_until_complete(coro)


if __name__ == '__main__':
    queue = asyncio.Queue()
    queue_schedule = asyncio.Queue()
    queue_log = asyncio.Queue()
    main()
    