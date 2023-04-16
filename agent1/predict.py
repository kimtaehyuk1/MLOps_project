'''
    usage:
        - install
            - pip install -r requirements.txt
'''

import boto3
import os
import tensorflow as tf
import urllib
import numpy as np
import time
import json
from tensorflow import keras
from PIL import Image



model = None
down_wei_name = 'densenet_Adam.h5'

def test_002(): 
    # 대기열 이름을 넣어서 대기열 URL 가져오기
    q_name = 'ai-project4-taehyuk-agent2'
    res = sqs.get_queue_url(QueueName=q_name)
    # 속도를 더 높이기 위해 주소변화가 없다면 하드코딩으로 진행 검토
    return res['QueueUrl']

def init_weight():
    if not os.path.exists('./' + down_wei_name): # 파일이 없다면
        # step 1. 최초 로드시 s3로부터 가중치 혹은 모델덤프 파일 다운로드(1회만)
        #        차후, 버전 관리(1.0버전(90%적용), 1.1버전(10%적용) -> 테스팅 -> 확대 및 교체)
        
        s3_client = boto3.client('s3')
        s3_client.download_file('ai-project4-taehyuk','models/' + down_wei_name, down_wei_name)
        print(f'{down_wei_name} 다운로드 완료')
    else:
        print(f'{down_wei_name} 이미 존재함')

# step 2. 모델로드
def load_model():
    global model
    model = tf.keras.models.load_model('./' + down_wei_name)



# step 3. 예측 및 결과 송신
#       3.1 case 1 : 로그저장, db에 저장 -> 푸시,
#       3.2 case 2 : 로그저장, sqs, ai-response-queue 큐 -> was에서 큐를 체크하면서 응답처리

def get_predict( url ):
    '''
    
        url : https://d3fv670o1z23k.cloudfront.net/data/xxxx.xxx 
            - CDN + 버킷상의 주소로 전달된다 -> sqs를 통해서 
    '''
    # 1. 예측할 이미지 url로 다운로드
    down_file_name = url.split("/")[-1]
    urllib.request.urlretrieve(url, down_file_name)
    # 2. 이미지를 에측당할 형태로 변환해주기.
    
    label_names = ['간장게장', '갈비구이', '갈비찜', '감자탕', '계란찜', '고등어구이',
    '김치찌개', '깍두기', '된장찌개', '떡볶이', '라면', '만두', '미역국',
    '배추김치', '보쌈', '불고기', '삼겹살', '삼계탕', '양념치킨',
    '잔치국수', '제육볶음', '족발', '짜장면', '짬뽕', '파전',
    '후라이드치킨']
    

    #이미지를 모델이 예측 가능하도록 가공
    x = keras.preprocessing.image.load_img('./' + down_file_name , target_size=(224, 224))
    x1 = keras.preprocessing.image.img_to_array(x)
    x = np.expand_dims(x1, axis=0)

    #예측
    result = model.predict(x)

    #결과값을 음식으로 맵핑시켜 초기화
    result_label = label_names[np.argmax(result)]
    result_li = f'{result_label},{down_file_name}'
    print(result_li)
    # 출력보기
    # print(result_label)
    
    # 4. 또다른 sqs에 결과값을 저장 -> 이유는 이 sqs만을 바라보는 agent를 만들것이다 = 그 agent의 역활은 결과값 받아서 db에 넘기는 역활 = 
    sqs.send_message(
            QueueUrl    = test_002(),
            MessageBody = json.dumps({"cmd":"predict", "data":f'{result_li}'})
        )
    
    
sqs = boto3.client('sqs')
def test_004():
    # 대기열큐를 특정 주기로 계속해서 체크, 모니터링, 감지한다. -> 딥러닝 에이전트에서 돌코드
    q_name = 'ai-project4-sqs-taehyuk'
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
    if res and ("Messages" in res): # 해당키가 존재하면 메시지가 존재하는것
        # 수신한 값을 기준 => 메시지가 존재하는 여부 체크 -> 메시지 삭제(큐에서) -> 예측처리 요청 진행 
        #print(res)
        # Body쪽 데이터를 추출하시오 => cmd, data 출력
        receipt_handle = res["Messages"][0]['ReceiptHandle']  # 메시지 고유값
        body = res["Messages"][0]["Body"]
        body = json.loads(body)
        #print(body['data'])
        standby_predict(body['data'])
        
        # 메시지 삭제 -> 큐에서 제거
        sqs.delete_message(
            QueueUrl=q_name,
            ReceiptHandle=receipt_handle
            )
        
        # 예측 수행을 지시 -> 예측 수행(딥러닝 에이전트(컨테이너) or 람다함수) 
        # ->  결과를 받아서 응답하는 큐에 메시지를 전송
    else:
        print('no message')

def standby_predict( key ):
    # sqs => 메시지 획득 => key획득 => 예측수행
    #key = 'KakaoTalk_20230224_151557154.jpg'
    cdn = 'https://d3fv670o1z23k.cloudfront.net'
    #url = f'{cdn}/data/{key}'
    url = f'{cdn}/{key}'  # s3에 있는 위치가 애초에 data/ 안에있었으니까
    get_predict(url)



if __name__=="__main__":
    init_weight()
    load_model()
    while True:
        test_004()
        time.sleep(1)


        