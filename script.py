from lxml import html
from concurrent.futures import ThreadPoolExecutor
import requests
import pandas as pd

def info_profile(username):
    def fetch(url):
        response = requests.get(url)
        return response.text

    def request(urls):
        with ThreadPoolExecutor() as executor:
            results = executor.map(fetch, urls)
        return results

    headers = {"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                            "(KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 "
                            "Chrome/71.0.3578.80 Safari/537.36"}

    url = f"https://letterboxd.com/{username}/films/"
    page = requests.get(url, headers=headers)
    tree = html.fromstring(page.content)

    pages = tree.xpath('/html/body/div[1]/div/div/section/div[2]/div[3]/ul/li/a')[-1].text

    page_urls = []
    for i in range(1, int(pages) + 1):
        page_urls += [f"https://letterboxd.com/{username}/films/page/" + str(i)]

    rs1 = request(page_urls)

    directors = {}
    film_urls = []

    for html_content in rs1:
        tree = html.fromstring(html_content)
        result = tree.xpath('/html/body/div[1]/div/div/section/ul/li/div')
        for film in result:
            link = "https://letterboxd.com" + film.attrib.get('data-target-link')
            film_urls += [link]

    rs = request(film_urls)
    directors = {}
    actors = {}

    for html_content in rs:
        tree = html.fromstring(html_content)
        director = tree.xpath('//div[@id="tabbed-content"]/div[@id="tab-crew"]/div[1]/p/a/text()')
        for d in director:
            directors[d] = directors.get(d, 0) + 1
        actor = tree.xpath('//div[@id="tab-cast"]/div/p/a/text()')
        actors_overflow = tree.xpath('//span[@id="cast-overflow"]')
        if actors_overflow:
            actor += tree.xpath('//span[@id="cast-overflow"]/a/text()')
        for a in actor:
            actors[a] = actors.get(a, 0) + 1

    df_directors = pd.DataFrame(directors.items(), columns=['Director', 'Times'])
    df_actors = pd.DataFrame(actors.items(), columns=["Actor", "Times"])
    df_actors = df_actors[df_actors['Actor'] != "Show All…"]

    df_directors = df_directors.sort_values(by="Times", ascending=False)[1:10]
    df_actors = df_actors.sort_values(by="Times", ascending=False)[1:10]
    
    return (df_directors, df_actors)