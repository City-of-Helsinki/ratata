import random


def random_park_nonexistent_id(url):
    return random.randint(10, 20)


def random_park_name(url):
    return random.choice(["Johnny Parkson", "Fancy Fruitville", "Temple of Oom"])


def validate_random_park(url, response):
    return response.text.find("Porkie Park") != -1

