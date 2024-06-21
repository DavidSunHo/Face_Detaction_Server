import cv2
import numpy as np
import sqlite3 as sql
from flask import Flask, request
from face_recognition_function.INPUTDATA import InputData
from face_recognition_function.DATAPRED import DataPred
import asyncio

app = Flask(__name__)
app.debug = False

input_util = InputData()
pred_util = DataPred()


def db_getOrderbyName(name):
   msg = ""
   try:
      with sql.connect("database.db") as con:
         #rows = cur.fetchall(); #레코드 단위로 데이터를 전달받음.
         cur = con.cursor()
         cur.execute("select * from guest where guest.name =?",(name,))
         msg = "getOrderbyName Record successfully added"
         return cur.fetchall(); #레코드 단위로 데이터를 전달받음.

   except:
      msg = "getOrderbyName Error in insert operation"
   
   finally: #try를 하던 except을 하던 finally는 무조건 한번 실행됨. 
      con.close() #db 닫음.
      print(msg)


def db_insert(name, groupname, data):
   try:
      with sql.connect("database.db") as con:
         #rows = cur.fetchall(); #레코드 단위로 데이터를 전달받음.
         cur = con.cursor()
         cur.execute("INSERT INTO guest (name,groupname,data) VALUES (?,?,?) ON CONFLICT(name) DO UPDATE SET groupname =?, data =?",(name, groupname, data, groupname, data))
         #cur.execute("INSERT INTO guest (name,groupname,data) VALUES (?,?,?)",(name, groupname, data))
         con.commit() 
         msg = "insert Record successfully added"

   except:
      con.rollback()
      msg = "insert Error in insert operation"
   
   finally: #try를 하던 except을 하던 finally는 무조건 한번 실행됨. 
      con.close() #db 닫음.
      print(msg)
      
@app.route('/Registration_page/', methods = ['POST', 'GET'])
def registrationUtil():
   
   if request.method == 'POST':
   
      # json 받아오기
      regist_info = request.get_json()
       
      # 받아온 데이터 처리
      label = regist_info['deviceID']
      groupname = regist_info['groupname']
      data = regist_info['data']
      frame = regist_info['imageByte']
      print('label : ' + label + ', groupname : ' + groupname + ', data : ' + data)
      #db_insert(label, groupname, data)
     
      regist_img = cv2.imdecode(np.fromstring(bytes(frame), dtype = np.uint8), cv2.IMREAD_COLOR)
      
      # while True:
      #    cv2.imshow("Sheep", regist_img)
      #    cv2.waitKey(0)
  
      #regist_img = cv2.resize(regist_img, (640, 480)
      #db_insert()
      #rgb_frame = cv2.cvtColor(regist_img, cv2.COLOR_BGR2RGB)
      input_util.update_check = True
      result = asyncio.run(input_util.registFunction(regist_img, label, groupname, data, False))
      if result == True:
         return {'result' : '1'}
      else :
         return {'result' : '0'}


@app.route('/FacePredict_page/', methods = ['POST', 'GET'])
def predictUtil():
   
   if request.method == 'POST':
      
      # json 받아오기
      regist_info = request.get_json()
      groupname = regist_info['groupname']
      frame = regist_info['imageByte']
      data = regist_info['data']
      # json to img
      regist_img = cv2.imdecode(np.fromstring(bytes(frame), dtype = np.uint8), cv2.IMREAD_COLOR)
      if input_util.update_check == True:
         asyncio.run(input_util.registFunction(None, None, groupname, None, True))
         input_util.update_check = False
         return {'result' : '0'}
      else:
         # 얼굴 예측
         if input_util.known_face_encodings != None:
            locations, names, userdata = asyncio.run(pred_util.face_pred(regist_img, input_util.known_face_encodings, input_util.known_face_names, input_util.known_face_userdata))
            # top, right, bottom, left, name
            locationDic = []
            
            for location in locations: 
               locationDic.append({
                  "top" :  f'{location[0] * 4}',
                  "right" : f'{location[1] * 4}',
                  "bottom" : f'{location[2] * 4}',
                  "left" : f'{location[3] * 4}'
               })
            return {'result' : '1', 'locations': locationDic, 'names' : names, 'data' : userdata}
         else:
            return {'result' : '0'}
      
    
if __name__ == '__main__':
   app.run(debug= False, threaded = True)