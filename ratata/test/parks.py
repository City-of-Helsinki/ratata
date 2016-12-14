import random


def random_park_nonexistant_id(url):
    return random.randint(10, 20)


def validate_random_park(url, response):
    return response.text.find("Porkie Park") != -1

