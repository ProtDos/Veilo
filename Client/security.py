import base64
import hashlib
import re
import secrets
import string
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from password_strength import PasswordPolicy
import uuid


def gen(length):
    try:
        al = string.ascii_uppercase + string.ascii_lowercase + string.digits + "^!§$%&/()=?*+#'-_.:;{[]}"  # creating a list of nearly every char
        """
        This code is outdated, because generating a random key isn't truly possible with the random module:
        - https://python.readthedocs.io/en/stable/library/random.html
        - https://www.youtube.com/watch?v=Nm8NF9i9vsQ
        bb = []  # init list
        for i in range(length):  # creating a random password based on var length
            bb.append(random.choice(al))
        return "".join(bb)
        """
        # A better solution is this:
        key_sequences = []
        for _ in range(length):
            key_sequences.append(secrets.choice(al))
        return "".join(key_sequences)
    except Exception as e:
        print("Error19:", e)


def strength_test(p):
    try:
        policy = PasswordPolicy()
        out = policy.password(p).strength()
        print(out)
        return [True if out > 0.35 else False]  # returning if password is good or not
    except Exception as e:
        print("Error20:", e)


def hash_pwd(password):
    try:
        salt = "%Up=gJDD8dwL^5+W4pgyprt*sd4QEKTM4nfkD$ZW&Zb_?j^wQUGS6kK?2VkfYy7zu?hnN%a9YU!wduhwnUbKpUe*g*Y#aT$=M2KsA6gMFpU+q!!Ha6HN6_&F3DCL@-gweA47FQyq9wu*yd&By%p-dKPGucfjs2-26He-rPZjLEvBn$a-NFeDHD-UP9A23@5@EtZ5+LmeBS@ZUHW9HDy9U@!3BM2^U5nrq+wUjesgEX^SvDgf8Qs8$kjzEacUGx@r"
        dataBase_password = password + salt
        hashed = hashlib.sha256(dataBase_password.encode())
        return hashed.hexdigest()
    except Exception as e:
        print("Error21:", e)


def hash_obj(obj):
    hashed = hashlib.sha256(obj.encode())
    return hashed.hexdigest()


class Encrypt:
    def __init__(self, message_, key):
        self.message = message_
        self.key = key

    def encrypt(self):
        password_provided = self.key
        password = password_provided.encode()
        salt = b'salt_'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        msg = self.message.encode()
        f = Fernet(key)
        msg = f.encrypt(msg)
        return msg


class Decrypt:
    def __init__(self, message_, key, verbose=True):
        self.message = message_
        self.key = key
        self.verbose = verbose

    def decrypt(self):
        try:
            self.key = self.key.encode()
            salt = b'salt_'
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.key))
            self.message = self.message.encode()
            f = Fernet(key)
            decoded = str(f.decrypt(self.message).decode())
            return decoded
        except:
            pass


class Encrypt_File:
    def __init__(self, message_, key):
        self.message = message_
        self.key = key

    def encrypt(self):
        password_provided = self.key
        password = password_provided.encode()
        salt = b'salt_'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=1000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        msg = self.message.encode()
        f = Fernet(key)
        msg = f.encrypt(msg)
        return msg


class Decrypt_File:
    def __init__(self, message_, key, verbose=True):
        self.message = message_
        self.key = key
        self.verbose = verbose

    def decrypt(self):
        try:
            self.key = self.key.encode()
            salt = b'salt_'
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=1000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.key))
            self.message = self.message.encode()
            f = Fernet(key)
            decoded = str(f.decrypt(self.message).decode())
            return decoded
        except:
            pass


def encode_file(file_path, key):
    with open(file_path, "rb") as image_file:
        return Encrypt(message_=base64.b64encode(image_file.read()).decode(), key=key).encrypt()


def decode_file(enc_string, name, key):
    with open(name, "wb") as image_file:
        a = base64.b64decode(Decrypt(message_=enc_string.decode(), key=key).decrypt())
        image_file.write(a)
        return a


def hashCrackWordlist(userHash):
    h = hashlib.sha256

    with open("assets/data/Wordlist.txt", "rb") as infile:
        for line in infile:
            try:
                line = line.strip()
                lineHash = h(line).hexdigest()

                if str(lineHash) == str(userHash.lower()):
                    return line.decode()
            except:
                pass

        return None


def is_uuid4(stri):
    pattern = re.compile(r'^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[8|9aAbB][a-f0-9]{3}-[a-f0-9]{12}$')
    if pattern.match(stri):
        try:
            uuid.UUID(stri)
            return True
        except ValueError:
            pass
    return False

