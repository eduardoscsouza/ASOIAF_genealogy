import requests

import pandas as pd
from bs4 import BeautifulSoup
from fake_useragent import UserAgent



AWOIAF_URL = "https://awoiaf.westeros.org"
HOUSES_LIST_URL = "https://awoiaf.westeros.org/index.php/List_of_Houses"
HOUSES_FILE = "houses.csv"



if __name__ == '__main__':
    df = pd.DataFrame(columns=["Name", "Region"])
    df.index.name = "URL"

    response = requests.get(HOUSES_LIST_URL, headers={"User-Agent": UserAgent().chrome}, timeout=10)
    soup = BeautifulSoup(response.content, "html.parser")

    tables = soup.find_all("table", {"class": "wikitable sortable plainrowheaders"})
    tables += soup.find_all("table", {"class": "wikitable sortable"})
    assert len(tables) == 6

    for table in tables[:-2]:
        for row in table.tbody.find_all("tr"):
            house = row.find_all("td")
            if len(house) < 2:
                continue

            url = house[1].find('a')
            url = f"{AWOIAF_URL}{url['href']}"
            name = house[1].text.strip()
            region = house[0].text.strip()
            df.loc[url] = name, region

    for row in tables[-2].tbody.find_all("tr"):
        house = row.find_all("td")
        if len(house) < 1:
            continue

        url = house[0].find('a')
        url = f"{AWOIAF_URL}{url['href']}"
        name = house[0].text.strip()
        region = "Yi Ti"
        df.loc[url] = name, region

    df = df.sort_values(by="Region")
    df.to_csv(HOUSES_FILE)
