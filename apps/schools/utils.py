import random
import string


def get_random_password(length=8):
    letters = string.ascii_letters
    return "".join(random.choice(letters) for i in range(length))
