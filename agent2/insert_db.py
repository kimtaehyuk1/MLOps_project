import boto3
import os
import tensorflow as tf
import urllib
import numpy as np
import time
import json
from tensorflow import keras
from PIL import Image

import pymysql as my

def db_inint():
    # mysql -u root -p
    # password:
    try:
        connection = my.connect(host            ='db',     # 여기에 db 컨테이너 명
                                    user        ='root',     
                                    password    ='1234',
                                    charset     ='utf8'
                                    )
    # mysql[None]:>
        with connection: # 커넥션은 with문을 나가면 자동으로 닫힌다
            with connection.cursor() as cur:  # 커서는 with문을 나가면 자동으로 닫힌다.
                # 1. 데이터베이스 생성
                cur.execute('create database if not EXISTS ml_db;')
                # 2. 커밋 -> 데이터베이스(물리적)에 변동을 가하면(db생성, 테이블 생성, 데이터입력/수정/삭제)
                connection.commit()
                # 3. 데이터베이스 사용 지정
                cur.execute('use ml_db;')
                # mysql[ml_db]:>
                # 4. 테이블 생성
                cur.execute('''
                    create table predict (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        result VARCHAR(256),
                        filename VARCHAR(256)
                    );
                ''')
                # 5. 커밋
                connection.commit()

    except Exception as e:
        print('접속 오류', e)


def db_insert( data,key ):
    try:
        # 커넥션
        connection = my.connect(host            ='db',    
                                    user        ='root',     
                                    password    ='1234',
                                    database    ='ml_db',
                                    charset     ='utf8',
                                    cursorclass =my.cursors.DictCursor
                                    )
        # mysql[None]:>
        with connection: # 커넥션은 with문을 나가면 자동으로 닫힌다
            with connection.cursor() as cur:
                sql = '''
                insert into predict (result,filename) VALUES (%s,%s);
            ''' 
                cur.execute(sql,(data,key))                                
                # 커밋
                connection.commit()
    except Exception as e:
        print(e)


sqs = boto3.client('sqs')


def test_004():
    # 대기열큐를 특정 주기로 계속해서 체크, 모니터링, 감지한다. -> 딥러닝 에이전트에서 돌코드
    q_name = 'ai-project4-taehyuk-agent2'
    res = sqs.receive_message(
            QueueUrl=q_name,
            AttributeNames=[
               'SentTimestamp'
            ],
            MessageAttributeNames=[
                'All',
            ],
            MaxNumberOfMessages=1, # 1개씩 가져오는 것으로 진행
            VisibilityTimeout=0,
            WaitTimeSeconds=0,
        )
    
    #print(res)
    if res and ("Messages" in res): # 해당키가 존재하면 메시지가 존재하는것
        # 수신한 값을 기준 => 메시지가 존재하는 여부 체크 -> 메시지 삭제(큐에서) -> 예측처리 요청 진행 
        #print(res)
        # Body쪽 데이터를 추출하시오 => cmd, data 출력
        receipt_handle = res["Messages"][0]['ReceiptHandle']  # 메시지 고유값 밑에서 삭제할때 들어감
        body = res["Messages"][0]["Body"]
        body = json.loads(body)
        img_title = body['data'].split(',')[0]
        img_key   = body['data'].split(',')[1]
        print(img_title, img_key)
        
        db_insert(img_title,img_key)
        
        # 메시지 삭제 -> 큐에서 제거
        sqs.delete_message(
            QueueUrl=q_name,
            ReceiptHandle=receipt_handle
            )
        
        # 예측 수행을 지시 -> 예측 수행(딥러닝 에이전트(컨테이너) or 람다함수) 
        # ->  결과를 받아서 응답하는 큐에 메시지를 전송
    else:
        print('no message')
    
    
    
if __name__=="__main__":
    db_inint()
    while True:
        test_004()
        time.sleep(1)