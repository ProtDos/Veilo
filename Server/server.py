import os
import re
import sqlite3
import threading

import pyotp
from flask import Flask, request, jsonify, session, send_file
import bcrypt
from password_strength import PasswordPolicy
from werkzeug.security import safe_join

app = Flask(__name__)
app.config["SECRET_KEY"] = str(os.urandom(50))

local_data = threading.local()

message_storage = []


def get_database_connection():
    if not hasattr(local_data, 'connection'):
        local_data.connection = sqlite3.connect('database.db')

        local_data.connection.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(50) NOT NULL,
        password VARCHAR(255) NOT NULL,
        secret_key VARCHAR(50) NOT NULL,
        authenticated INTEGER,
        bio VARCHAR(255),
        aboutme VARCHAR(255)
    )
""")

        local_data.connection.execute("""
            CREATE TABLE IF NOT EXISTS breach_overview (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(255),
                phone VARCHAR(255)
            )
        """)

    return local_data.connection


def strength_test(p):
    try:
        policy = PasswordPolicy()
        out = policy.password(p).strength()
        print(out)
        return [True if out > 0.35 else False]  # returning if password is good or not
    except Exception as e:
        print("Error20:", e)


def is_valid_phone(input_string):
    has_p = False
    for char in input_string:
        if char == "+":
            if input_string[0] != "+":
                return False
            if has_p:
                return False
            has_p = True
        if not char.isnumeric() and char != '+':
            return False
    return True


def is_valid_email(email):
    # Regular expression for email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if re.match(email_pattern, email):
        return True
    else:
        return False


get_database_connection()


################################# ERROR HANDELING #################################
@app.errorhandler(404)
def error_404(_):
    return jsonify({"error": "This page doesn't exist."}), 404


@app.errorhandler(405)
def error_405(_):
    return jsonify({"error": "This method is not allowed."}), 405


@app.errorhandler(500)
def error_500(_):
    return jsonify({"error": "Server Error."})


@app.errorhandler(403)
def error_403(_):
    return jsonify({"error": "Unauthorized."})


@app.errorhandler(400)
def error_400(_):
    return jsonify({"error": "I don't know."})


@app.errorhandler(415)
def error_415(_):
    return jsonify({"error": "Unsupported Media Type."})


################################# BASIC #################################
@app.route("/", methods=["POST", "GET"])
def basic():
    if request.method == 'POST':
        return jsonify({"status": "ok", "description": "Welcome to the API. More info on https://veilo.protdos.com"})
    else:
        return "<p>Welcome to the API. More info on https://veilo.protdos.com</p>"


################################# AUTHENTICATION #################################
@app.route('/register', methods=['POST'])
def register():
    """
    Creates an entry in the database with (username, salted+hashed password)

    Returns:
         JSON: Welcome _username_!
         Status code: 200

    Raises:
        Invalid Input: Malformed input / no JSON attached
        Missing Username: Missing Username
        Missing Password: Missing Password
        User already exists: User already exists in database

    Example Usage:
        POST /register
        DATA {"username": "new_username", "password": "SuperSecurePassword(Not_This)"}
    """

    try:
        print(request.json)
        print(request.data)
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        public = request.json.get('public', None)

        if not username:
            return jsonify({"error": "Missing Username", "code": 10000}), 400
        if not password:
            return jsonify({"error": "Missing Password", "code": 10001}), 400

        if not strength_test(password):
            return jsonify({"error": "Password isn't strong enough.", "description": "Use a stronger password with lower-, uppercase, digits and special characters.", "code": 10013}), 400

        salt = bcrypt.gensalt(14)

        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)

        # user = User(email=email, hash=hashed)
        # db.session.add(user)
        # db.session.commit()

        con = get_database_connection()

        cursor = con.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ?", [username])
        dat = cursor.fetchone()
        if dat:
            print(dat)
            return jsonify({"error": "User already exists", "code": 10009}), 401

        # secret_key = pyotp.random_base32()

        # Update the value in the SQLite database
        cursor.execute("INSERT OR IGNORE INTO users (username, password, secret_key, authenticated) VALUES (?, ?, 0, 0)",
                       (username, hashed))

        last_inserted_id = cursor.lastrowid  # TODO: Check if this is secure

        con.commit()
        con.close()

        with open(f"Publics/{last_inserted_id}.txt", "w") as fff:
            fff.write(public)

        print(last_inserted_id)

        return jsonify({"success": f'Welcome {username}!', "code": 11110, "id": last_inserted_id}), 200
    except AttributeError:
        return jsonify({"error": "Invalid Input. Check Json.", "code": 10006}), 400


@app.route('/login', methods=['POST'])
def login():
    """
    Creates an entry in the database with (username, salted+hashed password)

    Returns:
         JSON: Welcome _username_!
         Status code: 200

    Raises:
        Invalid Input: Malformed input / no JSON attached
        Missing Username: Missing Username
        Missing Password: Missing Password
        Missing Code: Missing Code
        Invalid code: The provided code is invalid.
        Invalid Credentials: The username/password combo isn't valid.
        User already exists: User already exists in database

    Example Usage:
        POST /login
        DATA {"username": "new_username", "password": "SuperSecurePassword(Not_This)"}
            OR
        DATA {"username": "new_username", "password": "SuperSecurePassword(Not_This)", "code": 123456}
    """

    try:
        print(request.json)
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        code = request.json.get("code", None)

        if not username:
            return jsonify({"error": "Missing Username", "code": 10000}), 400
        if not password:
            return jsonify({"error": "Missing Password", "code": 10001}), 400
        # if not code:
        #     return jsonify({"error": "Missing Code"}), 400

        con = get_database_connection()

        cursor = con.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ?", [username])
        dat = cursor.fetchone()
        if not dat:
            return jsonify({"error": "User not found", "code": 10002}), 404

        print(dat)
        if str(dat[3]) == "0":
            if bcrypt.checkpw(password.encode('utf-8'), dat[2]):
                cursor.execute("UPDATE users SET authenticated = 1 WHERE id = ?", (dat[0],))
                con.commit()
                con.close()
                session['user_id'] = dat[0]
                return jsonify({"success": f'Logged in, Welcome {username}!', "code": 11110, "id": dat[0]}), 200
            return jsonify({"error": "Invalid credentials.", "code": 10005}), 401
        if not code:
            return jsonify({"error": "Missing Code", "code": 10003}), 400

        totp = pyotp.TOTP(dat[3])
        if totp.verify(str(code)):
            if bcrypt.checkpw(password.encode('utf-8'), dat[2]):
                cursor.execute("UPDATE users SET authenticated = 1 WHERE id = ?", (dat[0],))
                con.commit()
                con.close()
                session['user_id'] = dat[0]

                messages = []
                for item in message_storage:
                    if item["recipient"] == dat[1]:
                        messages.append(item)
                        message_storage.remove(item)

                return jsonify({"success": f'Logged in, Welcome {username}!', "code": 11110, "id": dat[0], "outstanding_messages": messages}), 200
            return jsonify({"error": "Invalid credentials.", "code": 10005}), 401
        else:
            return jsonify({"error": f'Invalid code.', "code": 10004}), 401
    except AttributeError:
        return jsonify({"error": "Invalid Input. Check Json.", "code": 10006}), 401


################################# 2FA #################################
@app.route('/2fa/enable', methods=['POST'])
def enable_2fa():
    try:
        print(request.json)
        username = request.json.get('username', None)
        password = request.json.get('password', None)

        if not username:
            return jsonify({"error": "Missing Username", "code": 10000}), 400
        if not password:
            return jsonify({"error": "Missing Password", "code": 10001}), 400


        con = get_database_connection()

        cursor = con.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ?", [username])
        dat = cursor.fetchone()
        if not dat:
            return jsonify({"error": "User not found", "code": 10002}), 404

        print(dat)

        if bcrypt.checkpw(password.encode('utf-8'), dat[2]):
            if dat[3] != "0":
                return jsonify({"error": "Already enabled.", "description": "use /2fa/refresh to renew", "code": 10008}), 400
            secret_key = pyotp.random_base32()
            cursor.execute("UPDATE users SET secret_key = ?, authenticated = 0 WHERE id = ?", (secret_key, dat[0]))
            con.commit()
            con.close()
            return jsonify({"success": "Enabled 2FA", "secret_key": secret_key, "description": "Please login again.", "code": 11110}), 200
        return jsonify({"error": "Invalid credentials.", "code": 10005}), 401
    except AttributeError:
        return jsonify({"error": "Invalid Input. Check Json.", "code": 10006}), 401


@app.route('/2fa/verify', methods=['POST'])
def verify_2fa():
    try:
        print(request.json)
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        code = request.json.get("code", None)

        if not username:
            return jsonify({"error": "Missing Username", "code": 10000}), 400
        if not password:
            return jsonify({"error": "Missing Password", "code": 10001}), 400
        if not code:
            return jsonify({"error": "Missing Code", "code": 10003}), 400

        con = get_database_connection()

        cursor = con.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ?", [username])
        dat = cursor.fetchone()
        if not dat:
            return jsonify({"error": "User not found", "code": 10002}), 404

        if dat[3] == "0":
            return jsonify({"error": f'Please enable 2fa first.', "code": 10007}), 400

        totp = pyotp.TOTP(dat[3])
        if totp.verify(str(code)):
            if bcrypt.checkpw(password.encode('utf-8'), dat[2]):
                cursor.execute("UPDATE users SET authenticated = 1 WHERE id = ?", (dat[0],))
                con.commit()
                con.close()
                session['user_id'] = dat[0]
                return jsonify({"success": f'Successfully verified!', "code": 11110}), 200
            return jsonify({"error": "Invalid credentials.", "code": 10005}), 401
        else:
            return jsonify({"error": f'Invalid code.', "code": 10004}), 401
    except AttributeError:
        return jsonify({"error": "Invalid Input. Check Json.", "code": 10006}), 401


@app.route('/2fa/disable', methods=['POST'])
def disable_2fa():
    try:
        print(request.json)
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        code = request.json.get("code", None)

        if not username:
            return jsonify({"error": "Missing Username", "code": 10000}), 400
        if not password:
            return jsonify({"error": "Missing Password", "code": 10001}), 400
        if not code:
            return jsonify({"error": "Missing Code", "code": 10003}), 400

        con = get_database_connection()

        cursor = con.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ?", [username])
        dat = cursor.fetchone()
        if not dat:
            return jsonify({"error": "User not found", "code": 10002}), 404

        print(dat)

        if dat[3] == "0":
            return jsonify({"error": f'Please enable 2fa first.', "code": 10007}), 400

        totp = pyotp.TOTP(dat[3])
        if totp.verify(str(code)):
            if bcrypt.checkpw(password.encode('utf-8'), dat[2]):
                cursor.execute("UPDATE users SET authenticated = ?, secret_key = ? WHERE id = ?", (0, "0", dat[0]))
                con.commit()
                con.close()
                return jsonify({"success": f'Successfully disabled!', "code": 11110}), 200
            return jsonify({"error": "Invalid credentials.", "code": 10005}), 401
        else:
            return jsonify({"error": f'Invalid code.', "code": 10004}), 401
    except AttributeError:
        return jsonify({"error": "Invalid Input. Check Json.", "code": 10006}), 401


@app.route('/2fa/renew', methods=['POST'])
def renew_2fa():
    try:
        print(request.json)
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        code = request.json.get("code", None)

        if not username:
            return jsonify({"error": "Missing Username"}), 400
        if not password:
            return jsonify({"error": "Missing Password"}), 400
        if not code:
            return jsonify({"error": "Missing Code"}), 400

        con = get_database_connection()

        cursor = con.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ?", [username])
        dat = cursor.fetchone()
        if not dat:
            return jsonify({"error": "User not found"}), 404

        print(dat)

        if dat[3] == "0":
            return jsonify({"error": f'Please enable 2fa first.'}), 400

        totp = pyotp.TOTP(dat[3])
        if totp.verify(str(code)):
            if bcrypt.checkpw(password.encode('utf-8'), dat[2]):
                cursor.execute("UPDATE users SET authenticated = ?, secret_key = ? WHERE id = ?", (0, "0", dat[0]))
                con.commit()
                con.close()
                return jsonify({"success": f'Successfully disabled!'}), 200
            return jsonify({"error": "Invalid credentials."}), 401
        else:
            return jsonify({"error": f'Invalid code.'}), 401
    except AttributeError:
        return jsonify({"error": "Invalid Input. Check Json."}), 401


################################# USER MANAGEMENT #################################
@app.route("/change/password", methods=["POST"])
def change_password():
    old = request.json.get('old', None)
    new = request.json.get('new', None)

    if 'user_id' in session:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
        user = cursor.fetchone()

        if user and user[3] == "0":
            pass
        else:
            conn.close()
            return jsonify({"error": "Unauthorized access.", "code": 10010})

        if user and user[4] == 1:
            pass
        else:
            conn.close()
            return jsonify({"error": "Unauthorized access.", "code": 10010})

        print("Changing password.")
        print(user)
        print(old, new)

        if bcrypt.checkpw(old.encode(), user[2]):

            cursor.execute("UPDATE users SET password = ? WHERE id = ?", (bcrypt.hashpw(new.encode(), bcrypt.gensalt(14)), session['user_id'],))
            conn.commit()
            conn.close()

            return jsonify({"success": "Password Changed.", "code": 11110})
        return jsonify({'error': 'Invalid Password', "code": 10012})

    return jsonify({'error': 'Access denied', "code": 10011})


@app.route("/change/avatar", methods=["POST"])
def change_avatar():
    file = request.files['upload_file']


    if 'user_id' in session:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
        user = cursor.fetchone()

        if user and user[3] == "0":
            pass
        else:
            conn.close()
            return jsonify({"error": "Unauthorized access.", "code": 10010})

        if user and user[4] == 1:
            pass
        else:
            conn.close()
            return jsonify({"error": "Unauthorized access.", "code": 10010})

        file.save(f"Avatars/{session['user_id']}.png")

        return jsonify({"success": "Avatar Changed.", "code": 11110})

    return jsonify({'error': 'Access denied', "code": 10011})


@app.route("/change/username", methods=["POST"])
def change_username():
    new = request.json.get('new', None)

    if 'user_id' in session:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
        user = cursor.fetchone()

        if user and user[3] == "0":
            pass
        else:
            conn.close()
            return jsonify({"error": "Unauthorized access.", "code": 10010})

        if user and user[4] == 1:
            pass
        else:
            conn.close()
            return jsonify({"error": "Unauthorized access.", "code": 10010})

        cursor.execute("UPDATE users SET username = ? WHERE id = ?",
                       (new, session['user_id'],))
        conn.commit()
        conn.close()

        return jsonify({"success": "Username Changed.", "code": 11110})

    return jsonify({'error': 'Access denied', "code": 10011})


@app.route("/user/block", methods=["POST"])
def block():
    pass


@app.route("/user/unblock", methods=["POST"])
def unblock():
    pass


@app.route("/account/delete", methods=["POST"])
def delete():
    pass


################################# MESSAGING #################################
@app.route("/send", methods=["POST"])
def send_message():
    message = request.json.get('message', None)
    recipient = request.json.get('recipient', None)
    signature = request.json.get('signature', None)
    identity = request.json.get('identity', None)

    try:
        file = request.files["attachment"]
    except:
        file = None

    if message is None or recipient is None or signature is None or identity is None:
        return jsonify({'error': 'Incomplete data.', "code": 10017})


    print(message, recipient, signature, identity)

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (recipient,))
    user = cursor.fetchone()

    print(user)

    if user:
        message_storage.append({"message": message, "recipient": recipient, "signature": signature, "identity": identity})

        return jsonify({'success': 'Sent message', "code": 11110})
    return jsonify({'error': 'User not found', "code": 10002})


@app.route("/receive", methods=["POST"])
def receive_messages():
    print(session)
    if 'user_id' in session:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
        user = cursor.fetchone()

        print(user)
#
        # if user and user[3] == "0":
        #     pass
        # else:
        #     conn.close()
        #     return jsonify({"error": "Unauthorized access.", "code": 10010})

        if user and user[4] == 1:
            pass
        else:
            conn.close()
            return jsonify({"error": "Unauthorized access.", "code": 10010})

        messages = []
        for item in message_storage:
            if item["recipient"] == user[1]:
                messages.append(item)
                message_storage.remove(item)

        return jsonify({"success": "Access granted", "code": 11110, "messages": messages})

    return jsonify({'error': 'Access denied', "code": 10011})


@app.route("/user/public", methods=["POST"])
def get_public():
    try:
        idd = int(request.json.get('id', None))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid ID", "code": 10011}), 400

    base_directory = 'Avatars/'
    file_path = os.path.join(base_directory, f'{idd}.txt')

    if not file_path.startswith(base_directory):
        return jsonify({"error": "Invalid file path", "code": 10011}), 400
    
    file_path = f'Publics/{idd}.txt'

    return send_file(file_path, as_attachment=True)


@app.route("/user/exists", methods=["POST"])
def user_exists():
    username = request.json.get("username")

    con = get_database_connection()
    cursor = con.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", [username])
    dat = cursor.fetchone()
    if dat:
        return jsonify({"exists": True})
    return jsonify({"exists": False})


@app.route("/user/avatar", methods=["POST"])
def get_avatar():
    try:
        idd = int(request.json.get('id', None))
    except (ValueError, TypeError):
        return jsonify({"error": "Invlaid ID", "code": 10011})
    # TODO: Change Error codes / add to codes.txt for new codes

    base_directory = 'Avatars/'
    file_path = os.path.join(base_directory, f'{idd}.png')

    if not file_path.startswith(base_directory):
        return jsonify({"error": "Invalid file path", "code": 10011}), 400

    # file_path = f'Avatars/{idd}.png'
    file_path = safe_join("Avatars", f"{idd}.png")

    try:
        return send_file(file_path, as_attachment=True)
    except FileNotFoundError:
        return send_file("Avatars/Default/default.png", as_attachment=True)
    except Exception:
        return jsonify({"error": "File not found"})


@app.route("/user/username", methods=["POST"])
def get_username():
    pass


@app.route("/user/id", methods=["POST"])
def get_id():
    recipient = request.json.get('recipient', None)

    con = get_database_connection()

    cursor = con.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", [recipient])
    dat = cursor.fetchone()

    print(dat)


    if not dat:
        con.close()
        return jsonify({"error": "User not found", "code": 10002}), 404

    con.close()
    return jsonify({"success": "Found", "id": dat[0], "code": 11110})


@app.route("/group/create", methods=["POST"])
def create_group():
    pass


@app.route("/group/join", methods=["POST"])
def join_group():
    pass


@app.route("/group/delete", methods=["POST"])
def delete_group():
    pass


@app.route("/group/check", methods=["POST"])
def check_group():
    pass


@app.route("/breach", methods=["POST"])
def join_breach():
    try:
        print(request.json)
        email = request.json.get('email', None)
        phone = request.json.get('phone', None)

        if not email and not phone:
            return jsonify({"error": "Neither options send.", "code": 10014})

        if email:
            if not is_valid_email(email):
                return jsonify({"error": "Invalid email format.", "code": 10016})
        if phone:
            if not is_valid_phone(phone):
                return jsonify({"error": "Invalid phone format.", "code": 10015})

        print(email, phone)

        con = get_database_connection()

        cursor = con.cursor()


        cursor.execute(
            "INSERT OR IGNORE INTO breach_overview (email, phone) VALUES (?, ?)",
            (email, phone))

        con.commit()
        con.close()

        return jsonify({"success": "Added", "code": 11110})

    except:
        return jsonify({"error": "Invalid Input Check Json", "code": 10006})


################################# P2P #################################
@app.route("/p2p/get_connection", methods=["POST"])
def get_connection():
    pass


################################# PROTECTED FUNCTION #################################
@app.route('/testendpoint')
def test_endpoint():
    if 'user_id' in session:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
        user = cursor.fetchone()
        conn.close()

        if user and user[3] == "0":
            return jsonify({'message': 'Access granted to test endpoint'})

        if user and user[4] == 1:
            return jsonify({'message': 'Access granted to test endpoint'})

    return jsonify({'message': 'Access denied'})


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=80)
