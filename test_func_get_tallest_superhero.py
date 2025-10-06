import os
import logging
import pytest
import json
import requests

from func_get_tallest_superhero import get_tallest_superhero


logger = logging.getLogger(__name__)


@pytest.fixture(scope='module', autouse=True)
def setup_teardown(file_path):
    logger.info("Setup")
    session = requests.Session()
    logger.info("Get all data for check")
    with open(file_path, 'w+') as file:
        id = 1
        while True:
            res = session.get(f"https://www.superheroapi.com/api/{os.getenv('ACCESS_TOKEN', None)}/{id}")
            res = res.json()
            if res["response"] == "error" and res["error"] == "invalid id":
                break 
            json.dump(res, file)
            file.write('\n')
            id += 1
    
    yield

    logger.info("Teardown")
    if file_path.exists():
        logger.info(f"Remove file with data for check")
        os.remove(file_path)


@pytest.mark.positive
@pytest.mark.parametrize("gender,is_working", [
    ("Male", True),
    ("Male", False),
    ("Female", True),
    ("Female", False),
    ("mALe", True),
    ("-", True),
    ("-", False),
    ("Fimale", True),
    ("F(i&@male", True),
    ("Мужчина", True),
])
def test_correct_params(file_path, gender, is_working):
    res_return_func = get_tallest_superhero(gender, is_working)

    max_height = None
    tallest_superhero_id_list = []
    with open(file_path, 'r') as file:
        for line in file:
            item = json.loads(line)
            if item["appearance"]["gender"].lower() != gender.lower():
                continue
            if item["work"]["occupation"] and (item["work"]["occupation"] != "-") == is_working:
                if len(item["appearance"]["height"]) != 2:
                    continue
                if "cm" in item["appearance"]["height"][1]:
                    cur_height = float(item["appearance"]["height"][1].removesuffix(" cm"))
                elif "meters" in item["appearance"]["height"][1]:
                    cur_height = float(item["appearance"]["height"][1].removesuffix(" meters")) * 100
                else:
                    continue
                if not max_height or cur_height > max_height:
                    tallest_superhero_id_list.clear()
                    tallest_superhero_id_list.append(item)
                    max_height = cur_height
                elif max_height and cur_height == max_height:
                    tallest_superhero_id_list.append(item)

    assert res_return_func == tallest_superhero_id_list, (
        "Результат функции не верный: "
        f"Получено: {[i['id'] for i in res_return_func]}, "
        f"ожидалось: {[i['id'] for i in tallest_superhero_id_list]}")


@pytest.mark.negative
def test_very_long_gender():
    with pytest.raises(Exception) as e:
        res_return_func = get_tallest_superhero("FemaleMale" * 10000000, True)
    assert "Ошибка: переменная gender имеет слишком большое значение" in str(e.value), (
        f"{e}")


@pytest.mark.negative
def test_uncorrect_token(monkeypatch):
    logger.info("Смена ACCESS_TOKEN на неверный")
    monkeypatch.setenv("ACCESS_TOKEN", "1t1t1t1t1t1tt1t1")
    with pytest.raises(Exception) as e:
        res_return_func = get_tallest_superhero("Male", True)
    assert "Ошибка: access denied" in str(e.value), "Функция не провалидировала неверный токен"


@pytest.mark.negative
@pytest.mark.parametrize("gender,is_working", [
    (100, True),
    (None, True)
])
def test_uncorrect_type_gender(file_path, gender, is_working):
    with pytest.raises(TypeError) as e:
        res_return_func = get_tallest_superhero(gender, is_working)
    assert "Ошибка: переменная gender должна быть типа str" in str(e.value), (
        "Функция не провалидировала неверный параметр gender")


@pytest.mark.negative
@pytest.mark.parametrize("gender,is_working", [
    ("", True)
])
def test_empty_gender(gender, is_working):
    with pytest.raises(ValueError) as e:
        res_return_func = get_tallest_superhero(gender, is_working)
    assert "Ошибка: переменная gender пустая" in str(e.value), (
        "Функция не провалидировала пустой параметр gender")


@pytest.mark.negative
@pytest.mark.parametrize("gender,is_working", [
    ("   ", True)
])
def test_gender_with_space(gender, is_working):
    with pytest.raises(ValueError) as e:
        res_return_func = get_tallest_superhero(gender, is_working)
    assert "Ошибка: передано некорректное значение переменной gender" in str(e.value), (
        "Функция не провалидировала параметр gender")


@pytest.mark.negative
@pytest.mark.parametrize("gender,is_working", [
    ("Female", "False"),
    ("Female", None)
])
def test_uncorrect_type_is_working(gender, is_working):
    with pytest.raises(TypeError) as e:
        res_return_func = get_tallest_superhero(gender, is_working)
    assert "Ошибка: переменная is_working должна быть типа bool" in str(e.value), (
        "Функция не провалидировала неверный параметр is_working")
