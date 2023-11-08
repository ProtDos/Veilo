def set_private_key(username, password, private_key):
    with open("private_key.txt", "w") as file:
        file.write(str(private_key))


def get_private_key(username, password):
    with open("private_key.txt", "r") as file:
        return file.read()


def set_public_key(username, password, public_key):
    with open("public_key.txt", "w") as file:
        file.write(str(public_key))


def get_public_key(username, password):
    with open("public_key.txt", "r") as file:
        return file.read()

