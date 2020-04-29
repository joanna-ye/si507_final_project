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
RECIPE_LIST = []

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


def load_url(url, cache_dict):
    ''' Takes a url and access it using requests.
    Dumps the url result in to cache dictionary if it is not in there already.

    Parameters
    ----------
    url: string
        The url of a site
    cache_dict: dictionary
        The dictionary that stores all cache

    Returns
    -------
    soup
        The BeautifulSoup object after accessing a website
    '''
    if url in cache_dict.keys():
        soup = BeautifulSoup(cache_dict[url], 'html.parser')
    else:
        response = requests.get(url)
        html_text = response.text
        cache_dict[url] = html_text
        save_cache(cache_dict)
        soup = BeautifulSoup(html_text, 'html.parser')
    return soup


def explore_recipe(n):
    ''' Explores the popular recipes listed on the homepage.

    Parameters
    ----------
    n: int
        The number of times a user accessed the page; used as page number

    Returns
    -------
    None
    '''
    url = f"https://www.allrecipes.com/?page={n}"
    soup = load_url(url, CACHE_DICT)
    recipe = soup.find_all(class_="recipe-section fixed-grid")
    print("\nPrinting popular recipes...\n")
    print_recipe_list(recipe)


def search_recipe(keyword, cache_dict, n):
    ''' Searches for recipes based on the given keyword.

    Parameters
    ----------
    keyword: string
        The keyword a user wants to search for
    cache_dict: dictionary
        The dictionary that stores all cache
    n: int
        The number of times a user accessed the page; used as page number

    Returns
    -------
    None
    '''
    url = f"https://allrecipes.com/search/results/?wt={keyword}&sort=re&page={n}"
    soup = load_url(url, CACHE_DICT)
    recipe = soup.find_all(class_="recipe-section fixed-grid")
    print(f"\nPrinting search results related to '{keyword}'...\n")
    print_recipe_list(recipe)


def print_recipe_list(recipe):
    ''' Prints the recipes on a page. 20 results per page.
    Recipe and nutrition information is accessed at the same time.

    Parameters
    ----------
    recipe: list
        The list containing HTML tags

    Returns
    -------
    None
    '''
    n = len(RECIPE_LIST) + 1
    for r in recipe:
        for r in r.find_all(class_="fixed-recipe-card"):
            name = r.find(class_="fixed-recipe-card__title-link").text.strip()
            link = r.find(class_="fixed-recipe-card__info").find('a')['href']
            RECIPE_LIST.append([name, link])
            get_prep_info(name, link, CACHE_DICT)
            get_nutrition_info(name, link, CACHE_DICT)
            print(f"{n}. {name}")
            n += 1


def see_ingredient(name, url, cache_dict):
    ''' Fetches the ingredients needed for a given recipe.
    Ingredients are added to the corresponding database as they are accessed.

    Parameters
    ----------
    name: string
        The name of the recipe
    url: string
        The url of the recipe
    cache_dict: dictionary
        The dictionary that stores all cache

    Returns
    -------
    None
    '''
    soup = load_url(url, cache_dict)
    ingredients = soup.find_all(class_="ingredients-item-name")
    if ingredients == []:
        print("Sorry, the ingredients for this recipe is currently unavailable\n")
    else:
        print(f"\nThe ingredients needed for '{name}' are: ")
        for i in ingredients:
            ingredient = i.text.strip()
            print(ingredient)
            add_ingredient(name, ingredient)


def get_prep_info(name, url, cache_dict):
    ''' Searches for the preparation information of a given recipe and adds them to the database.

    Parameters
    ----------
    name: string
        The name of the recipe
    url: string
        The url of the recipe
    cache_dict: dictionary
        The dictionary that stores all cache

    Returns
    -------
    None
    '''
    prep_dict = {"prep": "N/A", "cook": "N/A", "total": "N/A", "additional": "N/A",
                 "Servings": "N/A", "Yield": "N/A"}
    soup = load_url(url, cache_dict)
    info = soup.find_all(class_="recipe-meta-item")
    for i in info:
        header = i.find(class_="recipe-meta-item-header").text.strip().rstrip(':')
        body = i.find(class_="recipe-meta-item-body").text.strip()
        prep_dict[header] = body
    add_recipe(name, prep_dict["prep"], prep_dict["cook"], prep_dict["total"],
               prep_dict["additional"], prep_dict["Servings"], prep_dict["Yield"])


def get_nutrition_info(name, url, cache_dict):
    ''' Searches for the nutrition information of a given recipe and adds them to the database.

    Parameters
    ----------
    name: string
        The name of the recipe
    url: string
        The url of the recipe
    cache_dict: dictionary
        The dictionary that stores all cache

    Returns
    -------
    None
    '''
    nutri_list = ["N/A", "N/A", "N/A", "N/A", "N/A", "N/A"]
    soup = load_url(url, cache_dict)
    nutrition = soup.find_all(class_="partial recipe-nutrition-section")
    if nutrition == []:
        pass
    else:
        info = nutrition[0].find(class_="section-body").text.strip()
        info = info.split(';')
        nutri_list[0] = info[0][:3]
        nutri_list[1] = info[1].strip()[:-10]
        nutri_list[2] = info[2].strip()[:-12]
        nutri_list[3] = info[3].strip()[:7]
        nutri_list[4] = info[3].strip()[24:-14]
        nutri_list[5] = info[4].strip()[:-8]
    add_nutrition(name, nutri_list[0], nutri_list[1], nutri_list[2],
                  nutri_list[3], nutri_list[4], nutri_list[5])


def print_nutrition(name):
    ''' Fetches the stored nutrition information from the database and prints them.

    Parameters
    ----------
    name: string
        The name of the recipe

    Returns
    -------
    None
    '''
    query = f'''
    SELECT * FROM Nutrition
    WHERE recipe = "{name}"
    '''
    conn = sqlite3.connect('recipe.sqlite')
    cur = conn.cursor()
    result = cur.execute(query).fetchall()[0]
    print(f"\nThe nutrition information of '{name}' is: ")
    print(f"Calorie: {result[1]}")
    print(f"Fat: {result[2]}")
    print(f"cholesterol: {result[3]}")
    print(f"Sodium: {result[4]}")
    print(f"Carbohydrates: {result[5]}")
    print(f"Protein: {result[6]}")


def add_recipe(name, prep_time="N/A", cook_time="N/A", total_time="N/A",
               additional_time="N/A", servings="N/A", output="N/A"):
    ''' Adds recipe information to the database when being called.

    Parameters
    ----------
    name: string
        The name of the recipe
    prep_time: string
        The preparation time needed for this recipe
    cook_time: string
        The cooking time needed for this recipe
    total_time: string
        The total time needed for this recipe
    additional_time: string
        The additional time needed for this recipe
    servings: int
        The number of people this recipe serves
    output: string
        The final yield of this recipe

    Returns
    -------
    None
    '''
    insert = "INSERT INTO Recipe VALUES(?,?,?,?,?,?,?)"
    data = (name, prep_time, cook_time, total_time, additional_time, servings, output)
    try:
        cur.execute(insert, data)
        conn.commit()
    except sqlite3.Error as error:
        print(error)


def add_nutrition(recipe, calorie="N/A", fat="N/A", cholesterol="N/A",
                  sodium="N/A", carbohydrates="N/A", protein="N/A"):
    ''' Adds nutrition information to the database when being called.

    Parameters
    ----------
    recipe: string
        The name of the recipe
    calorie: int
        The total calorie of this recipe
    fat: string
        The total fat (in grams) in this recipe
    cholesterol: string
        The total cholesterol (in grams) in this recipe
    sodium: string
        The total sodium (in milligrams) in this recipe
    carbohydrates: string
        The total carbohydrates (in milligrams) in this recipe
    protein: string
        The total protein (in grams) in this recipe

    Returns
    -------
    None
    '''
    insert = "INSERT INTO Nutrition VALUES(?,?,?,?,?,?,?)"
    data = (recipe, calorie, fat, cholesterol, sodium, carbohydrates, protein)
    try:
        cur.execute(insert, data)
        conn.commit()
    except sqlite3.Error as error:
        print(error)

def add_ingredient(recipe, ingredient):
    ''' Adds ingredient information to the database when being called.

    Parameters
    ----------
    recipe: string
        The name of the recipe
    ingredient: string
        The ingredients needed for this recipe

    Returns
    -------
    None
    '''
    insert = "INSERT INTO Ingredient VALUES(?,?)"
    data = (recipe, ingredient)
    try:
        cur.execute(insert, data)
        conn.commit()
    except sqlite3.Error as error:
        print(error)


def main_menu():
    ''' The main interface a user interacts with. Displays different menu options.

    Parameters
    ----------
    None

    Returns
    -------
    None
    '''
    menu = ["1. View more recipes", "2. View the ingredients of one recipe",
            "3. View the nutrition information of one recipe", "4. Go back to the last step", "5. Exit"]
    while True:
        print("\nHello! What would you like to do today?")
        print("1. Explore popular recipe")
        print("2. Search for recipe")
        print("3. Exit")
        user_input = input("Please choose one from the above options: ")
        if user_input.isnumeric() and int(user_input) in [1, 2, 3]:
            if int(user_input) == 1:
                page = 1
                explore_recipe(page)
                while True:
                    print("\nWhat would you like to do next?")
                    for m in menu:
                        print(m)
                    user_input = input("Please choose one from the above options: ")
                    if user_input.isnumeric() and int(user_input) in [1, 2, 3, 4, 5]:
                        if int(user_input) == 1:
                            page += 1
                            explore_recipe(page)
                        elif int(user_input) == 2:
                            while True:
                                number = input("\nPlease select the recipe you would like to see, or 'back' or 'exit': ")
                                if number == "back":
                                    break
                                if number == "exit":
                                    exit()
                                if number.isnumeric() and int(number) <= len(RECIPE_LIST):
                                    index = int(number)
                                    see_ingredient(RECIPE_LIST[index-1][0], RECIPE_LIST[index-1][1], CACHE_DICT)
                                else:
                                    print("\nInvalid input!")
                                    continue
                        elif int(user_input) == 3:
                            while True:
                                number = input("\nPlease select the recipe you would like to see, or 'back' or 'exit': ")
                                if number == "back":
                                    break
                                if number == "exit":
                                    exit()
                                if number.isnumeric() and int(number) <= len(RECIPE_LIST):
                                    index = int(number)
                                    print_nutrition(RECIPE_LIST[index-1][0])
                                else:
                                    print("\nInvalid input!")
                                    continue
                        elif int(user_input) == 4:
                            RECIPE_LIST.clear()
                            break
                        elif int(user_input) == 5:
                            print("Thank you for using the program. Goodbye!")
                            exit()
                    else:
                        print("\nInvalid input!")
                        continue
            elif int(user_input) == 2:
                page = 1
                keyword = input("\nPlease enter the keyword you want to search for: ")
                search_recipe(keyword, CACHE_DICT, page)
                while True:
                    print("\nWhat would you like to do next?")
                    for m in menu:
                        print(m)
                    user_input = input("Please choose one from the above options: ")
                    if user_input.isnumeric() and int(user_input) in [1, 2, 3, 4, 5]:
                        if int(user_input) == 1:
                            page += 1
                            search_recipe(keyword, CACHE_DICT, page)
                        elif int(user_input) == 2:
                            while True:
                                number = input("\nPlease select the recipe you would like to see, or 'back' or 'exit': ")
                                if number == "back":
                                    break
                                if number == "exit":
                                    print("Thank you for using the program. Goodbye!")
                                    exit()
                                if number.isnumeric() and int(user_input) <= len(RECIPE_LIST):
                                    index = int(number)
                                    see_ingredient(RECIPE_LIST[index-1][0], RECIPE_LIST[index-1][1], CACHE_DICT)
                                else:
                                    print("\nInvalid input!")
                                    continue
                        elif int(user_input) == 3:
                            while True:
                                number = input("\nPlease select the recipe you would like to see, or 'back' or 'exit': ")
                                if number == "back":
                                    break
                                if number == "exit":
                                    print("Thank you for using the program. Goodbye!")
                                    exit()
                                if number.isnumeric() and int(number) <= len(RECIPE_LIST):
                                    index = int(number)
                                    print_nutrition(RECIPE_LIST[index-1][0])
                                else:
                                    print("\nInvalid input!")
                                    continue
                        elif int(user_input) == 4:
                            RECIPE_LIST.clear()
                            URL_LIST.clear()
                            break
                        elif int(user_input) == 5:
                            print("Thank you for using the program. Goodbye!")
                            exit()
                    else:
                        print("\nInvalid input!")
                        continue
            elif int(user_input) == 3:
                print("Thank you for using the program. Goodbye!")
                exit()
        else:
            print("\nInvalid input!")
            continue


if __name__ == "__main__":
    CACHE_DICT = open_cache()
    conn = sqlite3.connect('recipe.sqlite')
    cur = conn.cursor()

    create_table_recipe = '''
        CREATE TABLE Recipe (
        name TEXT NOT NULL UNIQUE,
        prep_time TEXT,
        cook_time TEXT,
        total_time TEXT,
        additional_time TEXT,
        servings INT,
        output TEXT
        ) '''
    cur.execute("DROP TABLE IF EXISTS Recipe")
    cur.execute(create_table_recipe)

    create_table_nutrition = '''
        CREATE TABLE Nutrition (
        recipe TEXT,
        calorie INT,
        fat TEXT,
        cholesterol TEXT,
        sodium TEXT,
        carbohydrates TEXT,
        protein TEXT
        ) '''
    cur.execute("DROP TABLE IF EXISTS Nutrition")
    cur.execute(create_table_nutrition)

    create_table_ingredient = '''
        CREATE TABLE Ingredient (
        recipe TEXT,
        ingredient TEXT
        ) '''
    cur.execute("DROP TABLE IF EXISTS Ingredient")
    cur.execute(create_table_ingredient)

    # explore_recipe()
    # search_recipe("asparagus", CACHE_DICT)
    main_menu()
