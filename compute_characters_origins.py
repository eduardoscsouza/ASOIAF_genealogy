import numpy as np
import pandas as pd



CHARACTERS_FILE = "characters.csv"
CHARACTERS_ORIGINS_FILE = "characters_origins.csv"
HOUSES_ORIGINS_FILE = "houses_origins.csv"



def compute_origins(url, df, characters_df, houses_origins_df, origins_dict):
    if url in df.index:
        return df.loc[url, list(origins_dict.keys())].values

    if url in houses_origins_df.index:
        origin = houses_origins_df.loc[url, "Origin"]
        origin = origins_dict[origin]
        return origin

    if url == "Unknown":
        return origins_dict["Unknown"]

    father_origin = compute_origins(characters_df.loc[url, "Father"], df, characters_df, houses_origins_df, origins_dict)
    mother_origin = compute_origins(characters_df.loc[url, "Mother"], df, characters_df, houses_origins_df, origins_dict)

    origin = (father_origin + mother_origin) / 2.0
    origin = origin / np.sum(origin)    #Normalize to be 100% sure it adds to 1.0
    df.loc[url, list(characters_df.columns)] = characters_df.loc[url]
    df.loc[url, list(origins_dict.keys())] = origin

    return origin



if __name__ == '__main__':
    characters_df = pd.read_csv(CHARACTERS_FILE, index_col=0)
    houses_origins_df = pd.read_csv(HOUSES_ORIGINS_FILE, index_col=0)

    origins_dict = sorted(list(set(houses_origins_df["Origin"])))
    origins_dict = {origin: origin_vect for origin, origin_vect in zip(origins_dict, np.identity(len(origins_dict)))}

    df = pd.DataFrame(columns=list(characters_df.columns) + list(origins_dict.keys()))
    df.index.name = "URL"

    for url in characters_df.index:
        compute_origins(url, df, characters_df, houses_origins_df, origins_dict)

    df.reindex(characters_df.index)
    df.to_csv(CHARACTERS_ORIGINS_FILE)
