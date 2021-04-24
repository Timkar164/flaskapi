# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 14:56:15 2021

@author: timka
"""
import psycopg2
from psycopg2.extras import DictCursor
from flask import Flask, render_template, request
from psycopg2.errors import UndefinedColumn
from flask_cors import CORS
from hashlib import sha256
import smtplib
from os import urandom
import time

mailerLogin = 'dima160899@yandex.ru'
mailerPass = 'whzkcbkjuspbgnra'
host = 'ec2-54-164-22-242.compute-1.amazonaws.com'
port = '5432'
database = 'de8k09g3q8cu38'
user = 'froyqwzawvbzre'
password = '75a90d3b1363ad0f4b13ce32342cd6fe54c5348cd765ad8a5e6e0cdba3bd1cc4'
rez = ''
test = ''

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression


class Bot(object):
    def __init__(self):
        self.alphabet = ' 1234567890-йцукенгшщзхъфывапролджэячсмитьбюёqwertyuiopasdfghjklzxcvbnm'
        with open('casein.txt', encoding='utf-8') as f:
            content = f.read()
        blocks = content.split('\n')
        dataset = []
        for block in blocks:
            replicas = block.split('\\')[:2]

            if len(replicas) == 2:
                pair = [replicas[0], replicas[1]]

                if pair[0] and pair[1]:
                    dataset.append(pair)
        X_text = []
        y = []
        for question, answer in dataset[:10000]:
            X_text.append(question)
            y += [answer]
        self.vectorizer = CountVectorizer()
        X = self.vectorizer.fit_transform(X_text)
        self.clf = LogisticRegression()
        self.clf.fit(X, y)

    def clean_str(self, r):
        r = r.lower()
        r = [c for c in r if c in self.alphabet]
        return ''.join(r)

    def get_generative_replica(self, text):
        text_vector = self.vectorizer.transform([text])
        text_vector = text_vector.toarray()[0]
        question = self.clf.predict([text_vector])
        question = question[0]
        print(question)
        return question

    def main(self, command):
        command = command.lower()
        reply = self.get_generative_replica(command)
        return reply


def makesha(st):
    st = st + str(int(time.time()))
    return sha256(st.encode('utf-8')).hexdigest()


def sql_delet(table_name, param):
    conn = psycopg2.connect(dbname=database, user=user,
                            password=password, host=host)
    cursor = conn.cursor(cursor_factory=DictCursor)
    delet = "DELETE FROM " + str(table_name) + " WHERE id =" + str(param['id'])

    print(cursor.execute(delet))
    conn.commit()
    conn.close()
    cursor.close()
    return {'response': True}


def sql_insert(table_name, param):
    conn = psycopg2.connect(dbname=database, user=user,
                            password=password, host=host)
    cursor = conn.cursor(cursor_factory=DictCursor)
    insertstr = "INSERT INTO " + str(table_name) + " " + str(param[0]) + " VALUES " + str(param[1]) + " RETURNING id"
    cursor.execute(insertstr)
    _id = cursor.fetchone()[0]
    print(_id)
    conn.commit()
    conn.close()
    cursor.close()
    return {'response': True, 'id': str(_id)}


def sql_update(table_name, param):
    if param['id']:
        conn = psycopg2.connect(dbname=database, user=user,
                                password=password, host=host)
        cursor = conn.cursor(cursor_factory=DictCursor)
        update = "UPDATE " + str(table_name) + " SET " + str(param['colum']) + "  WHERE id =" + str(param['id'])
        cursor.execute(update)
        conn.commit()
        conn.close()
        cursor.close()
        return {'response': True}
    else:
        return {'response': False, 'items': 'error id'}


def sql_select(table_name, param):
    conn = psycopg2.connect(dbname=database, user=user,
                            password=password, host=host)
    cursor = conn.cursor(cursor_factory=DictCursor)
    try:
        if param:
            cursor.execute('SELECT * FROM ' + str(table_name) + ' WHERE ' + str(param))
        else:
            cursor.execute('SELECT * FROM ' + str(table_name))
        records = []
        I = True;
        while I:
            rez = cursor.fetchone()
            if rez != None:
                records.append(dict(rez))
            else:
                I = False
        conn.close()
        cursor.close()
        return {'response': True, 'items': records}
    except UndefinedColumn:
        conn.close()
        cursor.close()
        return {'response': False, 'items': 'error colum'}


def param_update(param):
    _id = None
    keys = list(param.keys())
    colum = ' '
    for key in keys:
        if key == 'id':
            _id = param[key]
        else:
            colum = colum + ' ' + str(key) + " = '" + str(param[key]) + "' ,"
    colum = colum[:-1]
    return {'colum': colum, 'id': _id}


def param_insert(param):
    keys = list(param.keys())
    colum = ' ( '
    values = '('
    for key in keys:
        colum = colum + ' ' + str(key) + ','
        values = values + " '" + str(param[key]) + "',"
    values = values[:-1]
    values += ')'
    colum = colum[:-1]
    colum += ')'
    return colum, values


def param_select(param):
    condition = ""
    keys = list(param.keys())

    for key in keys:
        param[key] = str(param[key])
        if ('[' and ']' in param[key]) or type(param[key]) == list:
            param[key] = eval(param[key])
            condition = condition + '('
            for par in param[key]:
                condition = condition + str(key) + ' = '
                condition = condition + "'" + str(par) + "'" + ' OR '
            condition = condition[:-3]
            condition += ') AND '

        else:
            condition = condition + '( ' + str(key) + ' = ' + "'" + str(param[key]) + "'" + ' ) AND '
    condition = condition[:-4]
    return condition


def api_select(name, args):
    return sql_select(str(name), param_select(dict(args)))


def api_insert(name, args):
    return sql_insert(str(name), param_insert(dict(args)))


def api_delet(name, args):
    return sql_delet(str(name), dict(args))


def api_update(name, args):
    return sql_update(str(name), param_update(dict(args)))


def api_log(log, pas):
    return sql_select('users', param_select({'log': log, 'pas': pas}))


def find_id(pole, znah, ardict):
    for i in ardict:
        if int(i[str(pole)]) == int(znah):
            return i

def is_token_valid(token):
    args = {'token': token};
    reg_user = api_select('reg_users', args)
    if not reg_user['items']:
        return False
    else:
        return bool(int(reg_user['items'][0]['token_valid']))

app = Flask(__name__)
CORS(app)

'''@app.route('/get_messages')
def indexmes():
 arg = dict(request.args)
 param = "( sender = '"+ str(arg['user'])+"' ) OR ( receiver = '"+str(arg['user'])+"' )"
 param = sql_select('messages',param_select({'id':}))
 users = sql_select('users','')
 for i in param['items']:
    st1=find_id('id',i['maker'],users['items'])
    st2=find_id('id',i['person'],users['items'])
    i['maker']=st1['name']
    i['person']=st2['name']
    i['img']=st1['img']

 return  {'response':True,'items':param['items']}'''


def send_emails(email_to, title, msg):
    server = smtplib.SMTP('smtp.yandex.ru', 587)
    server.ehlo()
    server.starttls()
    server.login(mailerLogin, mailerPass)

    message = f'From: {mailerLogin}\nTo: {email_to}\nSubject: {title}\n\n{msg}'
    server.sendmail(mailerLogin, email_to, message)
    server.quit()


@app.route('/login')
def log():
    arg = dict(request.args)
    email = arg['log']
    pas = arg['pas']
    user_item = api_select('reg_users', {'email': email, 'password': pas})
    print(user_item)
    if not user_item['items']:
        user_item = api_select('users', {'email': ' ' + email, 'pas': pas})
        print(user_item)
        if not user_item['items']:
            return {'response': False, 'error': 'User not found!'}
        else:
            user_item['items'][0]['user_type'] = 'main_user'
            return user_item
    else:
        role = api_select('roles', {"id": user_item['items'][0]["role"]})
        user_item['items'][0]['user_type'] = 'reg_user'
        user_item['items'][0]['role'] = role['items'][0]['name']
        return user_item


@app.route('/registration')
def reg():
    arg = dict(request.args)
    email = arg['email'] + ''
    token = urandom(16).hex()
    arg['token'] = token
    sql_insert('reg_users', param_insert(arg))
    send_emails(email, 'password change', 'http://localhost:4200/set_password?token=' + token)
    return {'response': True}

@app.route('/is_valid')
def is_valid():
    arg = dict(request.args)
    type_data = arg['type']
    data = arg['data']
    if type_data == 'getUserByToken':
        return {'response': True, 'is_valid': is_token_valid(data)}

@app.route('/get_action')
def indexact():
    global test
    arg = dict(request.args)
    _id = arg['id']
    action = sql_select('action', '')
    users = []
    for i in action['items']:
        users.append(int(i['users']))
    users = set(users)
    users = list(users)

    user = sql_select('users', param_select({'id': users}))
    user = user['items']
    test = user
    fr = sql_select('friends', param_select({'users': _id}))

    friend = []
    rez = []
    for i in action['items']:
        st = find_id('id', i['users'], user)
        i['name'] = st['name']
        i['img'] = st['img']
        rez.append(i)

    userss = sql_select('users', '')
    userss = userss['items']
    for i in fr['items']:
        try:
            st = find_id('id', i['friend'], userss)
            i['name'] = st['name']
            i['img'] = st['img']
            friend.append(i)
        except:
            print(i['friend'])

    return {'response': True, 'action': rez, 'friend': friend}


@app.route('/get_board')
def indexboard():
    param = sql_select('board', '')
    users = sql_select('users', '')
    for i in param['items']:
        st1 = find_id('id', i['maker'], users['items'])
        st2 = find_id('id', i['person'], users['items'])
        i['maker'] = st1['name']
        i['person'] = st2['name']
        i['img'] = st1['img']

    return {'response': True, 'items': param['items']}


@app.route('/get_idea')
def indexidea():
    param = sql_select('idea', '')
    users = sql_select('users', '')
    for i in param['items']:
        st1 = find_id('id', i['maker'], users['items'])

        i['maker'] = st1['name']

        i['img'] = st1['img']

    return {'response': True, 'items': param['items']}


@app.route('/get_kurs')
def indexkurs():
    param = sql_select('kurses', '')
    param = param['items']

    return {'response': True, 'my': param[1:7], 'rec': param[8:11], 'all': param}


@app.route('/get_friends')
def indexfr():
    arg = dict(request.args)
    name = arg['user']
    param = "( sender = '" + str(name) + "' ) OR ( receiver = '" + str(name) + "' )"
    return sql_select('messages', param)


@app.route('/get_message')
def indexm():
    arg = dict(request.args)
    name = arg['user']
    param = "( sender = '" + str(name) + "' ) OR ( receiver = '" + str(name) + "' )"
    param = sql_select('messages', param)
    param = param['items']

    users = []
    for i in param:
        users.append(int(i['sender']))
        users.append(int(i['receiver']))
    users = set(users)
    users = list(users)
    users.remove(int(name))
    if 200 in users:
        users.remove(200)
    rez = []
    ur = sql_select('users', '')
    for u in users:
        stu = find_id('id', u, ur['items'])
        st = {}
        for j in param:
            if int(j['sender']) == int(u) or int(j['receiver']) == int(u):
                st['last'] = j['text']
        st['name'] = stu['name']
        st['img'] = stu['img']
        st['id'] = stu['id']
        rez.append(st)

    return {'response': True, 'items': rez}


@app.route('/get_data')
def index():
    arg = dict(request.args)
    name = arg['table']
    del (arg['table'])
    print(arg)
    return api_select(str(name), arg)


@app.route('/set_data')
def index1():
    arg = dict(request.args)
    name = arg['table']
    del (arg['table'])
    return api_insert(str(name), arg)


@app.route('/delet_data')
def index2():
    arg = dict(request.args)
    name = arg['table']
    del (arg['table'])
    return api_delet(str(name), arg)


@app.route('/set_password')
def set_password():
    arg = dict(request.args)
    token = arg['token']
    passw = arg['password']
    if is_token_valid(token):
        conn = psycopg2.connect(dbname=database, user=user,
                                password=password, host=host)
        cursor = conn.cursor(cursor_factory=DictCursor)
        update = f"UPDATE reg_users  SET password = '{passw}', token_valid = '0'  WHERE token = '{token}'"
        cursor.execute(update)
        conn.commit()
        conn.close()
        cursor.close()
        return {'response': True}
    else:
        return {'response': False, 'error': "token is incorrect"}


@app.route('/update_data')
def index3():
    arg = dict(request.args)
    name = arg['table']
    del (arg['table'])
    return api_update(str(name), arg)


@app.route('/bot')
def bote():
    bott = Bot()
    arg = dict(request.args)
    com = arg['command']
    rez = bott.main(com)
    return {'response': True, 'bot': rez}


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)