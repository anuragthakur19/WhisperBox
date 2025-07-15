import random

def get_random_name():
    names = [
        "Naruto", "Sasuke", "Goku", "Luffy", "Sakura", "Zoro", "Tanjiro", "Nezuko",
        "Doraemon", "Shinchan", "Tom", "Jerry", "Mickey", "Donald", "Goofy", "Scooby",
        "Ash", "Pikachu", "Eren", "Levi", "Chopper", "Itachi", "Vegeta", "Nobita"
    ]
    return random.choice(names)
