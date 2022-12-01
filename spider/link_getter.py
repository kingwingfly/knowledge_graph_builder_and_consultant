import httpx
import asyncio
from parsel import Selector
import json


class UrlsLoader:
    def __init__(self, urls: dict, batch_size):
        self.urls = list(urls.items())
        self.batch_size = batch_size
        self.cur = 0
        self.len = len(urls)

    def __iter__(self):
        while True:
            if self.cur + self.batch_size < self.len:
                yield (self.index_urls(self.cur + i) for i in range(self.batch_size))
            else:
                yield (self.index_urls(i) for i in range(self.cur, self.len))
                break
            self.cur += self.batch_size

    def index_urls(self, index_num):
        return self.urls[index_num]


async def link_getter(source, url):
    start = 'https://baike.baidu.com'
    async with httpx.AsyncClient() as client:
        r = await client.get(url, follow_redirects=True,timeout=3)
        respone = Selector(r.text)
        links = respone.css('a[data-lemmaid]::attr(href)').getall()
        names = respone.css('a[data-lemmaid]::text').getall()
        results = dict(zip(names, map(lambda x: start + x, links)))
        await queue_schedule.put(source)
        return {source: results}


async def link_getter_main(url_root: dict, depth=3, batch_size=256, halt=1):
    for i in range(depth):
        print(f'进行到第{i+1}层')
        urls_loader = UrlsLoader(url_root, batch_size=batch_size)
        url_root, results_temp = {}, {}
        for batch in urls_loader:
            coros = (link_getter(source, url) for source, url in batch)
            results: list[dict[str, dict[str, str]]] = await asyncio.gather(*coros)
            for result in results:
                results_temp |= result
                for r in result.values():
                    url_root |= r
            await asyncio.sleep(halt)
        await queue.put(results_temp)

    await queue.put(None)
    await queue_schedule.put(None)


async def save_results(url_root):
    results_ultra = url_root
    while result := await queue.get():
        results_ultra |= result
    with open('./spider_results/urls.json', 'w', encoding='utf-8') as f:
        json.dump(results_ultra, f, ensure_ascii=False)
    print('Finished')


async def schedule():
    while source := await queue_schedule.get():
        print(f'{source} finished')


def main():
    depth = 2
    batch_size = 256
    # 每批次完成后停顿时间
    halt = 3
    url_root = {
        '数字孪生': 'https://baike.baidu.com/item/%E6%95%B0%E5%AD%97%E5%AD%AA%E7%94%9F/22197545?fr=aladdin'
    }
    loop = asyncio.new_event_loop()
    coros = [
        link_getter_main(url_root, depth, batch_size, halt),
        save_results(url_root),
        schedule(),
    ]
    coro = asyncio.wait(coros)
    loop.run_until_complete(coro)


if __name__ == '__main__':
    queue = asyncio.Queue()
    queue_schedule = asyncio.Queue()
    main()
