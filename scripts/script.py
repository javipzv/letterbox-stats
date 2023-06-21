from lxml import html
from concurrent.futures import ThreadPoolExecutor
import requests
import pandas as pd
import re

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

    error = False
    possible_error = tree.xpath("//body[@class='error message-dark']")
    if possible_error:
        error = True
        return (None, None, error)

    pages = tree.xpath('/html/body/div[1]/div/div/section/div[2]/div[3]/ul/li/a')[-1].text

    page_urls = []
    for i in range(1, int(pages) + 1):
        page_urls += [f"https://letterboxd.com/{username}/films/page/" + str(i)]

    rs1 = request(page_urls)

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

    df_directors = df_directors.sort_values(by="Times", ascending=False)[:10]
    df_actors = df_actors.sort_values(by="Times", ascending=False)[:10]

    return (df_directors, df_actors, error)

def info_profile_aux(username, comp = ""):
    def fetch(url):
        response = requests.get(url)
        return response.text

    def request(urls):
        with ThreadPoolExecutor() as executor:
            results = executor.map(fetch, urls)
        return results

    def transform_valoration(val):
        return val.count("★") + val.count("½")/2

    headers = {"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                            "(KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 "
                            "Chrome/71.0.3578.80 Safari/537.36"}
    url = f"https://letterboxd.com/{username}/films/"
    page = requests.get(url, headers=headers)
    tree = html.fromstring(page.content)

    error = False
    possible_error = tree.xpath("//body[@class='error message-dark']")
    if possible_error:
        error = True
        return (None, None, None, error)

    pages = tree.xpath('/html/body/div[1]/div/div/section/div[2]/div[3]/ul/li/a')[-1].text

    page_urls = []
    for i in range(1, int(pages) + 1):
        page_urls += [f"https://letterboxd.com/{username}/films/page/" + str(i)]

    rs1 = request(page_urls)

    film_urls = []
    film_titles = []
    films_score = []

    for html_content in rs1:
        tree = html.fromstring(html_content)
        result = tree.xpath('/html/body/div[1]/div/div/section/ul/li[@class="poster-container"]')
        for data in result:
            div = data.find('div')
            link = "https://letterboxd.com" + div.attrib.get('data-target-link')
            film_urls += [link]
            title = div.attrib.get('data-target-link')
            title = re.findall(".*\/(.*)\/$", title)[0]
            film_titles += [title]
            span = data.find('p/span')
            if span is not None:
                films_score += [span.text]
            else:
                films_score += ["No valorada"]

    df_valorations = pd.DataFrame({"title": film_titles,
                                  "score: " + comp: list(map(transform_valoration, films_score))})
    
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

    df_directors = df_directors.sort_values(by="Times", ascending=False)[:10]
    df_actors = df_actors.sort_values(by="Times", ascending=False)[:10]
        
    return (df_directors, df_actors, df_valorations, error)

def info_profile_only_films_score(username, comp = ""):
    def fetch(url):
        response = requests.get(url)
        return response.text

    def request(urls):
        with ThreadPoolExecutor() as executor:
            results = executor.map(fetch, urls)
        return results

    def transform_valoration(val):
        value = -1
        if val:
            if val.__contains__("★") or val.__contains__("½"):
                value = val.count("★") + val.count("½")/2
        return value

    headers = {"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                            "(KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 "
                            "Chrome/71.0.3578.80 Safari/537.36"}
    url = f"https://letterboxd.com/{username}/films/"
    page = requests.get(url, headers=headers)
    tree = html.fromstring(page.content)

    error = False
    possible_error = tree.xpath("//body[@class='error message-dark']")
    if possible_error:
        error = True
        return (None, error)

    pages = tree.xpath('/html/body/div[1]/div/div/section/div[2]/div[3]/ul/li/a')[-1].text

    page_urls = []
    for i in range(1, int(pages) + 1):
        page_urls += [f"https://letterboxd.com/{username}/films/page/" + str(i)]

    rs1 = request(page_urls)

    film_titles = []
    films_score = []

    for html_content in rs1:
        tree = html.fromstring(html_content)
        result = tree.xpath('/html/body/div[1]/div/div/section/ul/li[@class="poster-container"]')
        for data in result:
            div = data.find('div')
            title = div.attrib.get('data-target-link')
            title = re.findall(".*\/(.*)\/$", title)[0]
            film_titles += [title]
            span = data.find('p/span')
            if span is not None:
                films_score += [span.text]
            else:
                films_score += ["No valorada"]

    df_valorations = pd.DataFrame({"title": film_titles,
                                  "score: " + comp: list(map(transform_valoration, films_score))})

    return (df_valorations, error)

def compare_profiles(u1, u2):
    u1_dir, u1_act, u1_score, error = info_profile_aux(u1, u1)
    u2_dir, u2_act, u2_score, error = info_profile_aux(u2, u2)
    
    df_comp = pd.merge(u1_score, u2_score, on='title')

    return df_comp

def compare_profiles_only_score(u1, u2):
    def correct_titles(string):
        abc = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        result = string.replace("-", " ")
        if result[0] in abc:
            result = result[0].upper() + result[1:]
        if result == "Argentina 1985":
            return result
        coincidencia = re.search("(.*)\s(\d{4})", string=result)
        if coincidencia:
            add = re.sub(".*\s(\d{4})", f" ({coincidencia.group(2)})", result)
            result = coincidencia.group(1) + add
        return result

    u1_score, error = info_profile_only_films_score(u1, u1)
    u2_score, error = info_profile_only_films_score(u2, u2)
    
    df_comp = pd.merge(u1_score, u2_score, on='title')

    df_comp = df_comp.sort_values(by='title', ascending=True)

    df_comp['title'] = list(map(correct_titles, df_comp['title']))

    return df_comp