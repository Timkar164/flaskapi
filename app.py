# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 14:56:15 2021

@author: timka
"""
import psycopg2
from psycopg2.extras import DictCursor
from flask import Flask , render_template ,request
from psycopg2.errors import UndefinedColumn
from flask_cors import CORS

host = 'ec2-54-164-22-242.compute-1.amazonaws.com'
port = '5432'
database = 'de8k09g3q8cu38'
user = 'froyqwzawvbzre'
password = '75a90d3b1363ad0f4b13ce32342cd6fe54c5348cd765ad8a5e6e0cdba3bd1cc4'
rez=''


def sql_delet(table_name,param):
    
    conn = psycopg2.connect(dbname=database, user=user, 
                        password=password, host=host)
    cursor = conn.cursor(cursor_factory=DictCursor)
    delet = "DELETE FROM "+str(table_name)+" WHERE id ="+str(param['id'])
    
    print(cursor.execute(delet))
    conn.commit()
    conn.close()
    cursor.close()
    return {'response':True}
   

def sql_insert(table_name,param):
   conn = psycopg2.connect(dbname=database, user=user, 
                        password=password, host=host)
   cursor = conn.cursor(cursor_factory=DictCursor)
   insertstr = "INSERT INTO "+str(table_name)+" "+str(param[0])+" VALUES "+str(param[1]) + " RETURNING id"
   cursor.execute(insertstr)
   _id = cursor.fetchone()[0]
   print(_id)
   conn.commit()
   conn.close()
   cursor.close()
   return {'response':True,'id':str(_id)}
 
def sql_update(table_name,param):
   if param['id']:
    conn = psycopg2.connect(dbname=database, user=user, 
                        password=password, host=host)
    cursor = conn.cursor(cursor_factory=DictCursor)
    update = "UPDATE "+str(table_name)+" SET "+str(param['colum'])+"  WHERE id ="+str(param['id'])
    cursor.execute(update)
    conn.commit()
    conn.close()
    cursor.close()
    return {'response':True}
   else:
       return {'response':False,'items': 'error id'}

def sql_select(table_name,param):
   conn = psycopg2.connect(dbname=database, user=user, 
                        password=password, host=host)
   cursor = conn.cursor(cursor_factory=DictCursor)
   try:
    if param:
     cursor.execute('SELECT * FROM '+str(table_name)+' WHERE '+str(param))
    else:
     cursor.execute('SELECT * FROM '+str(table_name))
    records = cursor.fetchall()
    conn.close()
    cursor.close()
    return {'response':True, 'items':records}
   except UndefinedColumn:
     conn.close()
     cursor.close()
     return {'response':False,'items':'error colum'}
 
    
def param_update(param):
    _id=None
    keys = list(param.keys())
    colum=' '
    for key in keys:
        if key=='id':
            _id=param[key]
        else:
            colum=colum+' '+str(key)+" = '" + str(param[key])+"' ,"
    colum=colum[:-1]
    return {'colum':colum,'id':_id}


def param_insert(param):
    keys = list(param.keys())
    colum=' ( '
    values = '('
    for key in keys:
        colum=colum+' '+str(key)+','
        values=values+" '"+str(param[key])+"',"
    values=values[:-1]
    values+=')'
    colum=colum[:-1]
    colum+=')'
    return colum , values
    

def param_select(param):
    condition =""
    keys = list(param.keys())
    
    for key in keys:
        param[key]=str(param[key])
        if ('[' and ']' in param[key]) or type(param[key])==list:
         param[key]=eval(param[key])
         condition= condition +'(' 
         for par in param[key]:
             condition=condition + str(key)+ ' = '
             condition=condition + "'"+str(par)+"'"+ ' OR '
         condition=condition[:-3]
         condition+=') AND '
         
        else:
            condition=condition+'( ' + str(key)+ ' = ' + "'" + str(param[key]) + "'" + ' ) AND '
    condition=condition[:-4]
    return condition

def api_select(name,args):
    return sql_select(str(name),param_select(dict(args)))
  
def api_insert(name,args):
    return sql_insert(str(name),param_insert(dict(args)))

def api_delet(name,args):
    return sql_delet(str(name),dict(args))

def api_update(name,args):
    return sql_update(str(name),param_update(dict(args)))

app = Flask(__name__)
CORS(app)

@app.route('/get_data')
def index():
 return  api_select('first_table',request.args)

@app.route('/set_data')
def index1():
 return  api_insert('first_table',request.args)

@app.route('/delet_data')
def index2():
 return  api_delet('first_table',request.args)

@app.route('/update_data')
def index3():
 return  api_update('first_table',request.args)


if __name__=="__main__":
    app.run(host='0.0.0.0', port=8000)