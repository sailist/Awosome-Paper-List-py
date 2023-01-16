import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from collections import Counter


def iter_paper(c):
    tmp = []
    for i in c:
        if i.name == 'dt':
            yield tmp
            tmp = []
        if i != '\n':
            tmp.append(i)
    yield tmp

class Crawl:
    def __init__(self, year, links) -> None:
        self.dic = {}
        self.year = year
        self.links = links

    def parse(self):
        for link in self.links:
            res = requests.get(link)
            content = res.content.decode()
            soup = BeautifulSoup(content, features="lxml")
            paper_group = list(iter_paper(soup.dl.children))

            for g in paper_group:
                root = 'https://openaccess.thecvf.com/'

                if len(g) == 0 or len(g) == 1 or g[0].name != 'dt':
                    continue

                href = g[0].a

                title = href.get_text().strip()
                url = urljoin('https://openaccess.thecvf.com/',
                              href.attrs['href'])

                attrs = {'link': url}

                refs = g[2].find_all('a')
                for r in refs:
                    ctt = r.get_text()
                    if ctt in {'pdf', 'supp'}:
                        rurl = urljoin(root, r.attrs['href'])
                    elif ctt in {'arXiv', 'video'}:
                        rurl = r.attrs['href']
                    elif ctt in {'bibtex'}:
                        continue
                    else:
                        print('ignore', ctt, f'of {r}')
                        pass
                    
                    attrs[ctt] = rurl

                self.append_item(self.year, title, attrs)

    def start(self):
        self.parse()
        self.write()

    def append_item(self, year, title, attrs=None, type=None):
        if type is not None:
            self.dic.setdefault((year, type), []).append([title, attrs])
        else:
            self.dic.setdefault((year, ''), []).append([title, attrs])

    def write(self):
        cc = Counter()
        for k, v in self.dic.items():
            year = k[0]
            k = '_'.join([i for i in k if i is not None]).strip('_')
            res = []
            for i, (title, attrs) in enumerate(v, start=1):
                if attrs is None:
                    res.append(f'{i}. {title}')
                else:
                    attrs = ', '.join(
                        [f"[{k}]({v})" for k, v in attrs.items()])
                    res.append(f'{i}. {title} | {attrs}')
            cc[year] += len(res)
            with open(f'{k}.md', 'w') as w:
                w.write('\n'.join(res))
                print(f' - write {len(res)} papers for {k}.')
        for k, v in cc.items():
            print(f'total {v} papers in {k}.')



Crawl('2023', [
    'https://openaccess.thecvf.com/WACV2023',
]).start()

Crawl('2022', [
    'https://openaccess.thecvf.com/WACV2022',
]).start()

Crawl('2021', [
    'https://openaccess.thecvf.com/WACV2021',
]).start()

Crawl('2020', [
    'https://openaccess.thecvf.com/WACV2020',
]).start()
