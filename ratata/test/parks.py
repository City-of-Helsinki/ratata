import random


def random_park_id(url):
    return random.randint(0, 10)


def validate_random_park(url, response):
    return response.contains("park")

