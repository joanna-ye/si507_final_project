#################################
##### Name: Joanna Ye ###########
##### Uniqname: jiayuan #########
#################################

from bs4 import BeautifulSoup
import requests
import json
import sqlite3

CACHE_FILENAME = "project_cache.json"
CACHE_DICT = {}

def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    If the cache file doesn't exist, creates a new cache dictionary

    Parameters
    ----------
    None

    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk

    Parameters
    ----------
    cache_dict: dict
        The dictionary to save

    Returns
    -------
    None
    '''
    cache_file = open(CACHE_FILENAME, 'w')
    dumped_json_cache = json.dumps(cache_dict)
    cache_file.write(dumped_json_cache)
    cache_file.close()

def explore_recipe():
    response = requests.get("https://www.allrecipes.com/")
    html_text = response.text
    soup = BeautifulSoup(html_text, 'html.parser')
    print_recipe_list(soup)


def search_recipe(keyword, cache_dict):
    url = f"https://allrecipes.com/search/results/?wt={keyword}&sort=re"
    if url in cache_dict.keys():
        print("Using cache")
        soup = BeautifulSoup(cache_dict[url], 'html.parser')
        print_recipe_list(soup)
    else:
        print("Fetching")
        response = requests.get(url)
        html_text = response.text
        cache_dict[url] = html_text
        save_cache(cache_dict)
        soup = BeautifulSoup(html_text, 'html.parser')
        print_recipe_list(soup)


def print_recipe_list(soup):
    recipe = soup.find_all(class_="recipe-section fixed-grid")
    for r in recipe:
        for r in r.find_all(class_="fixed-recipe-card"):
            name = r.find(class_="fixed-recipe-card__title-link").text
            print(name)

def see_ingredient(url, cache_dict):
    if url in cache_dict.keys():
        print("Using cache")
        soup = BeautifulSoup(cache_dict[url], 'html.parser')
        # print_ingredient_list(soup)
    else:
        print("Fetching")
        response = requests.get(url)
        html_text = response.text
        cache_dict[url] = html_text
        save_cache(cache_dict)
        soup = BeautifulSoup(html_text, 'html.parser')
        # print_ingredient_list(soup)

def print_ingredient(soup):
    pass


def add_recipe(id, name, time="N/A", calorie="N/A", fat="N/A", carbs="N/A",
                     fiber="N/A", sugar="N/A", protein="N/A", video="N/A"):
    insert = "INSERT INTO Recipe VALUES(?,?,?,?,?,?,?,?,?,?)"
    data = (id, name, time, calorie, fat, carbs, fiber, sugar, protein, video)
    try:
        cur.execute(insert, data)
        conn.commit()
    except sqlite3.Error as error:
        print(error)


def add_ingredient(recipe_id, name, amount="N/A", price="N/A"):
    insert = "INSERT INTO Ingredient VALUES(?,?,?,?)"
    data = (recipe_id, name, amount, price)
    try:
        cur.execute(insert, data)
        conn.commit()
    except sqlite3.Error as error:
        print(error)


if __name__ == "__main__":
    CACHE_DICT = open_cache()
    conn = sqlite3.connect('tasty.sqlite')
    cur = conn.cursor()

    create_table_recipe = '''
        CREATE TABLE Recipe (
        recipe_id INT PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        time TEXT,
        calorie INT,
        fat TEXT,
        carbs TEXT,
        fiber TEXT,
        suger TEXT,
        protein TEXT,
        video TEXT
        ) '''
    cur.execute("DROP TABLE IF EXISTS Recipe")
    cur.execute(create_table_recipe)

    create_table_ingredient = '''
        CREATE TABLE Ingredient (
        recipe_id INT,
        ingredient TEXT,
        amount TEXT,
        price INT
        ) '''
    cur.execute("DROP TABLE IF EXISTS Ingredient")
    cur.execute(create_table_ingredient)

    # explore_recipe()
    # search_recipe("asparagus", CACHE_DICT)

    add_recipe(1, 'Glazed Chicken Skewers', 'Under 30 minutes', '307', '12g', '25g', '0g', '21g', '21g')
    add_recipe(2, 'Jazzy Fried Chicken', calorie='656', fat='29g', carbs='48g', fiber='1g', sugar='4g', protein='50g')
    add_ingredient(1, 'boneless, skinless chicken thighs, cut into 1-inch (2 1/2 cm) chunks', '1 lb')
    add_ingredient(1, 'green onion, sliced into 1-inch (2 1/2 cm) pieces', '1 cup')
    add_ingredient(1, 'canola oil', '3 tablespoons')
    add_ingredient(1, 'soy glaze', '1/2 cup')
    add_ingredient(1, 'green onion, thinly sliced, to garnish')
    add_ingredient(2, 'McCormick Jazzy Spice Blend', '2 tablespoons')
    add_ingredient(2, 'kosher salt', '1 tablespoon')
    add_ingredient(2, 'freshly ground black pepper', '2 tablespoons')
    add_ingredient(2, 'buttermilk', '4 cups')
    add_ingredient(2, 'bone-in, skin-on chicken thighs and drunmsticks', '4 lb')
