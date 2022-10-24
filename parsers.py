"""Parsers for different websites"""

import pandas as pd
from bs4 import BeautifulSoup


def ycombinator_parser(text: bytes) -> pd.DataFrame:
    """Parser for news.ycombinator.com"""
    soup = BeautifulSoup(text, "html.parser")

    articles = soup.find_all(name="tr", attrs={"class": "athing"})
    scores = soup.find_all(name="td", attrs={"class": "subtext"})

    titles = []
    links = []
    points = []
    for article in articles:
        art = article.find("span", attrs={"class": "titleline"})
        titles.append(art.getText())
        links.append(art.find("a", recursive=False).get("href"))
    for score in scores:
        scr = score.find("span", attrs={"class": "score"})
        if scr is None:
            points.append(None)
        else:
            points.append(scr.getText())

    data_dict = {"Title": titles, "Link": links, "Points": points}
    data_frame = pd.DataFrame.from_dict(data_dict, orient="index").T

    return data_frame


def grahamcluley_parser(text: bytes) -> pd.DataFrame:
    """Parser for grahamcluley.com"""
    soup = BeautifulSoup(text, "html.parser")

    articles = soup.find_all(name="h2", attrs={"class": "entry-title"})

    titles = []
    links = []
    for article in articles:
        art = article.find("a", recursive=False)
        titles.append(art.getText())
        links.append(art.get("href"))

    data_dict = {"Title": titles, "Link": links}
    data_frame = pd.DataFrame.from_dict(data_dict, orient="index").T

    return data_frame
