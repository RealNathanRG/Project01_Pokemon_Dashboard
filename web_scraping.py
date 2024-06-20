import re
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup


def movesets(name: str):
    """
    A function to pull
    :param name: NAME OF THE POKEMON WE ARE SEARCHING FOR
    :return: RETURNS 2 TABLES FOR LEARNSET AND TM/HM
    """
    url = f'https://bulbapedia.bulbagarden.net/wiki/{name}_(Pok%C3%A9mon)/Generation_VI_learnset'
    html = requests.get(url)
    s = BeautifulSoup(html.content, 'html.parser')

    # 1. Get Table names
    # table_names = s.find_all("h4")
    # table_names = [i.text for i in table_names]

    # 2. Get tables
    all_tables = s.find_all('table', class_='sortable')
    headers = [table.find_all("th") for table in all_tables]
    titles = [[] for i in range(len(headers))]
    for j, k in enumerate(headers):
        for i in k:
            title = i.text
            title = " ".join(title.split())
            titles[j].append(title)

    def get_power(pwr: str):
        """
        Extract move power from string
        :param pwr:
        :return:
        """
        if len(pwr) == 6:
            get_pwr = pwr[:3]
        elif pwr[1] == "0":
            get_pwr = np.nan
        else:
            get_pwr = pwr[1:3]

        return get_pwr

    def get_accuracy(acc: str):
        """
        Extract move power from string
        :param acc:
        :return:
        """
        if len(acc) == 7:
            get_acc = acc[:3]
        else:
            get_acc = acc[1:3]

        if re.search(r"\D", get_acc):
            get_acc = np.nan

        return get_acc

    moveset = []
    for j, rows in enumerate(all_tables[0:2]):
        df = pd.DataFrame(columns=titles[j])

        for k, i in enumerate(rows.find_all("tr")):
            row = i.find_all("td")
            # print(row)
            new_row = [new_row.text for new_row in row]
            # print(new_row)
            if len(new_row) == 0:
                continue
            new_row = pd.Series(new_row, index=titles[j])
            # print(new_row)
            df.loc[k] = new_row

        for n in df:
            df[n] = df[n].apply(lambda x: x.replace('\n', ''))
        if "Level" in df.columns:
            df["Level"] = df["Level"].apply(lambda x: x[:3] if len(x) == 6 else x[:2])
            df["Pwr."] = df["Pwr."].apply(lambda x: get_power(x))
            df["Acc."] = df["Acc."].apply(lambda x: get_accuracy(x))
            # df["Acc."] = df["Acc."].apply(lambda x: x if re.match(r"[0-9]", x) else np.nan)
            df["Appeal"] = df["Appeal"].apply(lambda x: re.sub('[^0-9]', '', x))
            df["Jamming"] = df["Jamming"].apply(lambda x: re.sub('[^0-9]', '', x))

        if "ORAS" in df.columns:
            df["ORAS"] = df["ORAS"].apply(lambda x: x[1:4] if len(x) == 6 else x[1:3])
            df["Pwr."] = df["Pwr."].apply(lambda x: get_power(x))
            df["Acc."] = df["Acc."].apply(lambda x: re.findall(r"\}\}(.+)", x)[0][:-1])
            df["Acc."] = df["Acc."].apply(lambda x: x if re.match(r"[0-9]", x) else np.nan)
            df["Appeal"] = df["Appeal"].apply(lambda x: re.sub('[^0-9]', '', x))
            df["Jamming"] = df["Jamming"].apply(lambda x: re.sub('[^0-9]', '', x))
            df.rename(columns={"ORAS": "Level"}, inplace=True)
            df.drop(["XY"], axis=1, inplace=True)
            df.dropna(subset=["Level"], axis=0, inplace=True)

        if "TM" in df.columns:
            df.drop([""], axis=1, inplace=True)
            df["Pwr."] = df["Pwr."].apply(lambda x: get_power(x))
            df["Acc."] = df["Acc."].apply(lambda x: re.findall(r"\}\}(.+)", x)[0][:-1])
            df["Acc."] = df["Acc."].apply(lambda x: x if re.match(r"[0-9]", x) else np.nan)
            df["Appeal"] = df["Appeal"].apply(lambda x: re.sub('[^0-9]', '', x))
            df["Jamming"] = df["Jamming"].apply(lambda x: re.sub('[^0-9]', '', x))
            df = df[df["Move"].str.contains("XY") == False]
            df["Move"] = df["Move"].apply(lambda x: re.sub("ORAS", "", x))

        moveset.append(df)

    return moveset


# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
# moves = movesets("Feraligatr")
# print(moves)

def stats_table(gen: int):
    """
    :param: gen: generation of Pokémon.
    :return: List of all Pokémon with their stats data.
    """

    def generation(gen: int):
        """
        Return which table code needed for that generation.
        :param gen: generation of Pokémon.
        :return: Generation number string for URL
        """
        if gen == 1:
            return "I"
        elif gen in [2, 3, 4, 5]:
            return "II-V"
        elif gen == 6:
            return "VI"
        elif gen == 7:
            return "VII"
        elif gen == 8:
            return "VIII"
        elif gen == 9:
            return "IX"
        else:
            return TypeError

    url = f'https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_base_stats_(Generation_{generation(gen)})'
    html = requests.get(url)
    s = BeautifulSoup(html.content, 'html.parser')

    table = s.find('table', class_='sortable')
    headers = table.find_all("th")
    titles = []
    for i in headers:
        title = i.text
        title = " ".join(title.split())
        titles.append(title)

    stats = []
    df = pd.DataFrame(columns=titles)
    for k, i in enumerate(table.find_all("tr")):
        row = i.find_all("td")
        # print(row)
        new_row = [new_row.text for new_row in row]
        if len(new_row) == 0:
            continue

        new_row = pd.Series(new_row, index=titles)
        # print(new_row)
        df.loc[k] = new_row

    for n in df.keys():
        df[n] = df[n].apply(lambda x: x.replace('\n', ''))

    df["Pokémon"] = df["Pokémon"].apply(
        lambda x: [x, x] if x in ["Mr. Mime", "Mime Jr."] or " " not in x else x.split(maxsplit=1))
    df[["Pokémon", "form_name"]] = pd.DataFrame(df["Pokémon"].to_list(), index=df.index)
    df[["#", "HP", "Attack", "Defense", "Sp. Attack", "Sp. Defense", "Speed", "Total"]] = df[
        ["#", "HP", "Attack", "Defense", "Sp. Attack", "Sp. Defense", "Speed", "Total"]].apply(
        lambda col: col.astype("int"))
    df["Average"] = df.Average.astype("float")
    df.rename(columns={"#": "id"}, inplace=True)
    df.drop(columns=[""], inplace=True)
    return df


# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
# x = stats_table(6)
# print(x)


def get_attributes(name: str):
    """

    :param name:
    :return:
    """

    url = f"https://bulbapedia.bulbagarden.net/wiki/{name}_(Pok%C3%A9mon)"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")

    table = soup.find_all('td', class_='roundy')
    headers = [t.find("b") for t in table]

    def catch(h):
        try:
            return h.text
        except:
            return None

    headers = [catch(header) for header in headers]

    # print(headers)

    table_index = [index for index, value in enumerate(headers) if value is not None]
    # print(headers[table_index[12]])

    long = []
    for i in table:
        row = i.find_all("table", class_="roundy")
        long.append(row)

    attributes = []
    for i in long:
        new_row = [r.text for r in i]
        new_row = [r.replace("\n\n\n\n\n", "") for r in new_row]

        attributes.append(new_row)

    dict = {headers[index]: attributes[index] for index in table_index}

    return dict


# Abilities
def get_abilities(name: str):
    dict = get_attributes(name)
    if "Ability" in list(dict.keys()):
        dict["Abilities"] = dict["Ability"]
    abilities = [x.replace(u"\xa0", " ") for x in dict["Abilities"][0].split("\n") if x != "" and "Cacophony" not in x]
    if re.match(r"(.*)Gen [A-Z]+\+.*", abilities[0]):
        abilities[0] = re.findall(r"(.*)Gen [A-Z]+\+.*", abilities[0])[0]
    return abilities


# Gender Ratio
def get_gender_ratio(name: str):
    dict = get_attributes(name)
    return re.findall(r"(\d*\.?\d\% male|\d*\.?\d\% female|Gender unknown)", dict["Gender ratio"][0])


# Catch Rate
def get_catch_rate(name: str):
    dict = get_attributes(name)
    return re.findall(r"(\d+ \(\d+\.*\d*\%\))", dict["Catch rate"][0])[0]


# Breeding
def get_breeding(name: str):
    dict = get_attributes(name)
    breeding_group = (dict["Breeding"][0]
                      .replace(u"\xa0", " ")
                      .strip()
                      .split(" and "))
    for i, eg in enumerate(breeding_group):
        if re.match(r"(.*)Gen [A-Z]+\+.*", eg):
            breeding_group[i] = re.findall(r"(.*)Gen [A-Z]+\+.*", eg)[0]
        if "No Eggs Discovered" in eg and len(breeding_group) > 1:
            breeding_group.remove(eg)

    breeding_group[0] = breeding_group[0].replace(name, "")

    if "Egg not obtainable" in dict["Breeding"][-1]:
        steps = "Egg not obtainable"
    else:
        steps = dict["Breeding"][1].strip().replace(u"\xa0", " ")
        steps = re.findall(r"(\d+)", steps)[0]

    return breeding_group, steps


# Height
def get_height(name: str):
    dict = get_attributes(name)
    height = [x for x in dict["Height"][0].split("\n") if x != ""]
    form = height[2::3]
    inches = height[::3]
    meters = height[1::3]
    return {form[i]: (inches[i], meters[i]) for i in range(len(height[::3]))}


# Weight
def get_weight(name: str):
    dict = get_attributes(name)
    weight = [x for x in dict["Weight"][0].split("\n") if x != ""]
    form = weight[2::3]
    lbs = weight[::3]
    kg = weight[1::3]
    return {form[i]: (lbs[i], kg[i]) for i in range(len(weight[::3]))}


# Mega Stone

def get_mega_stone(name: str):
    dict = get_attributes(name)
    return [x.replace("[[|]]", "None") for x in dict["Mega Stone"][0].split("\n") if x != ""]


# Base experience yield

def get_base_experience_yield(name: str):
    dict = get_attributes(name)
    return [re.findall(r"\d*", x)[0] for x in dict["Base experience yield"][0].split("\n") if x != ""][-1]


# Leveling rate
def get_leveling_rate(name: str):
    dict = get_attributes(name)
    return dict["Leveling rate"][0].strip()


# EV yield

def get_ev_yield(name: str):
    dict = get_attributes(name)
    evs = [x for x in dict["EV yield"][0].split("\n") if x != ""]
    ev_total = evs[0].split(" ")
    ev_set1, ev_set2, ev_set3, ev_set4 = evs[1:8], evs[8:15], evs[15:22], evs[22:]
    ev_set1[1:] = [int(re.findall(r"\d+", x)[0]) for x in ev_set1[1:]]
    ev_set2[1:] = [int(re.findall(r"\d+", x)[0]) for x in ev_set2[1:]]
    ev_set3[1:] = [int(re.findall(r"\d+", x)[0]) for x in ev_set3[1:]]
    ev_set4[1:] = [int(re.findall(r"\d+", x)[0]) for x in ev_set4[1:]]
    if sum(ev_set2[1:]) == 0:
        ev_set2[1:] = ev_set1[1:]
        if sum(ev_set3[1:]) == 0:
            ev_set3[1:] = ev_set1[1:]
            if sum(ev_set4[1:]) == 0:
                ev_set4[1:] = ev_set1[1:]

    return {ev_total[0]: ev_total[1], ev_set1[0]: ev_set1[1:], ev_set2[0]: ev_set2[1:], ev_set3[0]: ev_set3[1:],
            ev_set4[0]: ev_set4[1:]}


# Pokédex color
def get_dex_color(name: str):
    dict = get_attributes(name)
    color = re.findall(r"([a-zA-Z]+)Other forms may have other colors|([a-zA-Z]+)", dict["Pokédex color"][0])[0]
    dex_color = [x for x in color if x != ""][0]
    return dex_color


# Base friendship
def get_base_friendship(name: str):
    dict = get_attributes(name)
    return dict["Base friendship"][0].strip()


# External Links
