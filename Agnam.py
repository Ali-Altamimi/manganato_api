import json
from rich import print
from rich.console import Console
from rich.progress import track
from rich.prompt import Prompt

import requests
from bs4 import BeautifulSoup

from IPython.display import Image, display


class Manga:
    """
    This class scrap 'manganato' data.
    Prameters:
        name: Manga name
        url_page: it takes the url page that you want to scrap from 'manganato'
    """
    URL_SEARCH = 'https://manganato.com/search/story/'
    def __init__(self, name=None, url_page=None):
        self.name = name.replace(' ', '_') if name is not None else None
        self.url_page = url_page
        self.logo = None
        self.alternative =None
        self.authors =None
        self.status =None
        self.genres =None
        self.chapters = None
        
        if name is not None:
            self.search(self.name)
        
        
    def search(self, name=None)-> str:
        if name is None:
            name = Prompt.ask("Enter Manga's Name", default="One Piece")
        URL = self.URL_SEARCH + name.replace(' ', '_')
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find(attrs="search-story-item")
        self.name = results.find('a')['title']
        self.url_page = results.find('a', href=True)['href']
        self.details()
        
    def details(self):
        genre = []
        list_chapter = list()
        page = requests.get(self.url_page)
        soup = BeautifulSoup(page.content, "html.parser")
        # info panel      
        panel_story_info = soup.find(attrs='panel-story-info')
        # info panel left      
        self.logo = panel_story_info.find('img')['src']
        # info panel right      
        story_info_right =panel_story_info.find(attrs='story-info-right')
        self.alternative = [x.strip() for x in story_info_right.find_all(attrs='table-value')[0].h2.get_text().split('; ')]
        self.authors = story_info_right.find_all(attrs='table-value')[1].a.get_text()
        self.status = story_info_right.find_all(attrs='table-value')[2].get_text()
        for text in story_info_right.find_all(attrs='table-value')[3].find_all('a'):
            genre.append(text.get_text())
        self.genres = genre
        
        # Chapter panel
        story_chapter_list =soup.find(attrs='panel-story-chapter-list')
        for chapter in story_chapter_list.find_all('a')[::-1]:
            dic_chapter = dict()
            dic_chapter['title'] = chapter.get_text()
            dic_chapter['url'] = chapter['href']
            list_chapter.append(dic_chapter)
        self.chapters = list_chapter

        print('[green]Success.')
    def get_chapter(self, url:str=None, num:int=None):
        if url is not None:
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")
            results = [x['src'] for x in soup.find(class_='container-chapter-reader').find_all('img')]
        else:
            page = requests.get(self.chapters[num]['url'])
            soup = BeautifulSoup(page.content, "html.parser")
            results = [x['src'] for x in soup.find(class_='container-chapter-reader').find_all('img')]
        
        return results

    def display(self, chapter:[str]=None):
        for image_url in chapter:
            headers = {
                'DNT': '1',
                'Referer':'https://readmanganato.com/',
                'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
                'sec-ch-ua-platform': "macOS",
#                 'cache-control': "no-cache",
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36'
                }
            r = requests.get(image_url, headers=headers)

            display(Image(r.content))

    def __repr__(self):
        return self.json()
    def json(self):
        return json.dumps(self.__dict__,ensure_ascii=False, indent=4)
