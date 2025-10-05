import os
import requests
import logging

logger = logging.getLogger("func_get_tallest_superhero")


def request_wrapper(session: requests.Session, endpoint, white_list = None):
    if not white_list:
        white_list = []
    base_url = f"https://www.superheroapi.com/api/{os.getenv('ACCESS_TOKEN', None)}"
    res = session.get(f"{base_url}/{endpoint}")
    if not res:
        logger.debug(f"Ошибка обращения по url {base_url}/{endpoint}: {res.text}")
        raise Exception(f"{res.text}")
    
    res = res.json()
    if res["response"] == "error":
        error = res["error"]
        if error in white_list:
            return None
        else:
            raise Exception(f"Ошибка: {error}")
    return res

def get_tallest_superhero(gender: str, is_working: bool) -> list:
    """
    Функцию принимает на вход пол и наличие работы (булево значение)
    и возвращает по этим критериям самого высокого героя (если несколько супергероев с одним ростом, то всех)
    """
    if not isinstance(gender, str):
        raise TypeError("Ошибка: переменная gender должна быть типа str")
    if not gender:
        raise ValueError("Ошибка: переменная gender пустая")
    if not isinstance(is_working, bool):
        raise TypeError("Ошибка: переменная is_working должна быть типа bool")
    
    tallest_superhero_id_list = []
    max_height = None
    id = 1

    session = requests.Session()

    while id:
        res = request_wrapper(session, f"{id}/work", ["invalid id"])
        if not res:
            break
        current_work = res["occupation"] != "-" 
        if current_work == is_working:
            res = request_wrapper(session, f"{id}/appearance")
            if res["gender"].lower() == gender.lower():
                if len(res["height"]) != 2:
                    continue
                if "cm" in res["height"][1]:
                    cur_height = float(res["height"][1].removesuffix(" cm"))
                elif "meters" in res["height"][1]:
                    cur_height = float(res["height"][1].removesuffix(" meters")) * 100
                else:
                    continue
                if not max_height or cur_height > max_height:
                    tallest_superhero_id_list.clear()
                    tallest_superhero_id_list.append(id)
                    max_height = cur_height
                elif max_height and cur_height == max_height:
                    tallest_superhero_id_list.append(id)
        id += 1
        logger.debug(f"{id}")
    logger.debug(f"id Cамого высокого супергероя с заданными критериями: {tallest_superhero_id_list}")
    
    tallest_superhero_list = []
    for id in tallest_superhero_id_list:
        res = request_wrapper(session, id)
        tallest_superhero_list.append(res)
    return tallest_superhero_list
