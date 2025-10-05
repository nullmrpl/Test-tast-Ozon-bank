import os
import requests
import json
import logging

logger = logging.getLogger("func_get_tallest_superhero")


def get_tallest_superhero(gender: str, is_working: bool) -> list:
    """
    Функцию принимает на вход пол и наличие работы (булево значение)
    и возвращает по этим критериям самого высокого героя (если несколько супергероев с одним ростом, то всех)
    """
    base_url = f"https://www.superheroapi.com/api/{os.getenv('ACCESS_TOKEN', None)}"
    tallest_superhero_list = []
    id = 1
    while id:
        res = requests.get(f"{base_url}/{id}/work")
        if not res:
            logger.debug(f"Ошибка обращения по url {base_url}/{id}/work: {res.text}")
            break
        res = res.json()
        if res["response"] == "error":
            logger.debug(f"{res['error']}: id={id}")
            break
        current_work = res["occupation"] != "-" 
        if current_work == is_working:
            res = requests.get(f"{base_url}/{id}/appearance")
            res = res.json()
            if res["gender"].lower() == gender.lower():
                if not tallest_superhero_list or res["height"][1] > tallest_superhero_list[0]["appearance"]["height"][1]:
                    res = requests.get(f"{base_url}/{id}")
                    res = res.json()
                    tallest_superhero_list.clear()
                    tallest_superhero_list.append(res)
                elif tallest_superhero_list and res["height"][1] == tallest_superhero_list[0]["appearance"]["height"][1]:
                    tallest_superhero_list.append(res)
        id += 1
        logger.debug(f"{id}")
    logger.debug(f"Cамый высокий супергерой с заданными критериями: {tallest_superhero_list}")
    return tallest_superhero_list
