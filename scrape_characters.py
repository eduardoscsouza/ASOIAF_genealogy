import requests

import pandas as pd
from bs4 import BeautifulSoup
from fake_useragent import UserAgent



AWOIAF_URL = "https://awoiaf.westeros.org"
CHARACTERS_LIST_URL = "https://awoiaf.westeros.org/index.php/List_of_characters"
CHARACTERS_FILE = "characters.csv"
HOUSES_FILE = "houses.csv"



def get_parent(table, parent_type, houses):
    parent = table.find('th', string=parent_type)
    parent = parent if parent is not None else table.find('th', string=parent_type+"s")
    if parent is not None:
        parent = parent.find_next_sibling('td').find('a')
        parent = f"{AWOIAF_URL}{parent['href']}" if ((parent is not None) and (parent.has_attr('href'))) else None

    else:
        parent = table.find('th', string="Allegiance")
        parent = parent if parent is not None else table.find('th', string="Allegiances")
        if parent is not None:
            parent = parent.find_next_sibling('td').find('a')
            parent = f"{AWOIAF_URL}{parent['href']}" if ((parent is not None) and (parent.has_attr('href'))) else None
            parent = parent if parent in houses else None

    return parent

def get_characters_list():
    response = requests.get(CHARACTERS_LIST_URL, headers={"User-Agent": UserAgent().chrome}, timeout=10)
    soup = BeautifulSoup(response.content, "html.parser")

    characters = soup.find("div", {"class": "mw-parser-output"})
    characters = characters.find_all('li')
    characters = [character.find_all('a') for character in characters]
    characters = [character[0] for character in characters if len(character) > 0]
    characters = [f"{AWOIAF_URL}{character['href']}" for character in characters]

    return characters

if __name__ == '__main__':
    df = pd.DataFrame(columns=["Name", "Father", "Mother"])
    df.index.name = "URL"

    houses = set(pd.read_csv(HOUSES_FILE)["URL"])
    queue = get_characters_list()
    while queue:
        url = queue.pop(0)
        if url in df.index:
            continue

        response = requests.get(url, headers={"User-Agent": UserAgent().chrome}, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        name = soup.find('h1').text.strip()
        df.loc[url] = name, "Unknown", "Unknown"

        table = soup.find('table', {'class': 'infobox'})
        if table is not None:
            for parent_type in ["Father", "Mother"]:
                parent = get_parent(table, parent_type, houses)
                if parent is not None:
                    df.loc[url, parent_type] = parent
                    if parent not in houses:
                        queue.append(parent)

    df.to_csv(CHARACTERS_FILE)
