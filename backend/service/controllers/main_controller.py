from flask import render_template, request, redirect, url_for, session
from service.controllers import bp_main as main
import os
import torch
from tensorflow.keras.preprocessing.sequence import pad_sequences
from transformers import BertTokenizer
import random
import numpy as np
import boto3
import pymysql as my

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')

# 버킷 리스트 획득
def test_001():
    bks = [ bk.name for bk in s3.buckets.all() ]
    #print(bks)
    return bks


def select_food(filename):  # 함수화 하기
    '''
        아이디, 비밀번호를 넣어서 회원여부를 체크하는 함수
        parameter
            - uid : 아이디
            - upw : 비밀번호
        returns
            - 회원인경우 
                - {'name': '게스트', 'uid': 'guest', 'regdate': datetime.datetime(2023, 3, 24, 13, 2, 31)}
            - 비회원인경우, 디비측 오류
                - None
    '''
    pre_res = None
    while True:
        connection = None
        row = None # 로그인 쿼리 수행 결과를 담는 변수
        try:    
            connection = my.connect(host        ='db',
                                    user        ='root',     
                                    password    ='1234',
                                    database    ='ml_db',    
                                    cursorclass =my.cursors.DictCursor
                                    )
            
            with connection.cursor() as cursor:
                # 파라미터는 %s표시로 순서대로 세팅된다 '값' => ''는 자동으로 세팅된다
                sql = '''
                    SELECT 
                        * 
                    FROM 
                        predict
                '''
                # execute() 함수의 2번 인자가 파라미터 전달하는 자리, 튜플로 표현
                cursor.execute( sql )
                row = cursor.fetchall() # 결과셋중 한개만 가져온다 => 단수(리스트가 아닌 단독타입:딕셔너리)
                
                if row:
                    for n in range(len(row)):
                        if filename in row[n]['filename']:
                            pre_res = row[n]['result']
                        
                        
        except Exception as e:
            print('접속 오류', e)
        else:
            print('접속시 문제 없었음')
        finally:    # 예외 사항이든 아니든 무조건 수행
            if connection:
                connection.close()
                
        if pre_res:
            break
    
    return pre_res



image_path = "imgs"

# ~/main
@main.route('/')
def home():
    if not 'uid' in session:
        return redirect(url_for('auth_bp.login'))
    return render_template('index.html')
    

# ~/main/densenet
@main.route('/densenet', methods=['GET','POST'])
def densenet():
    return render_template('densenet.html')


@main.route('/res2', methods=['GET','POST'])
def res2():
    if request.method == 'POST':
        file = request.files['file']
        filename = file.filename
        # if not os.path.exists('./backend/service' + image_path):
        #     print('폴더 생성')
        #     print( os.makedirs('./' + image_path) )
        file.save(os.path.join(image_path, filename))
        print(filename)
        text = "저장완료"
        
        # 연결된 s3로 업로드
        def test_003(bks):
            for bk in bks:
                if bk == 'ai-project4-taehyuk':
                    s3_client.upload_file(f'./imgs/{filename}',bk,f'data/{filename}')
        
        bks = test_001()
        # 파일업로드
        test_003(bks)
        
        
        result = select_food(filename)
        

        return result
    

# 간단한 표현문장을 적어주면 -> 감정을 분석하여 -> 감정에 맞는 음식 중 랜덤으로 추천이 나감
device = torch.device("cpu")
model1 = torch.load('./bert_final_text_model.pt',map_location=device) 

# 입력 데이터 변환
def convert_input_data(sentences):

    # BERT의 토크나이저로 문장을 토큰으로 분리
    tokenized_texts = [tokenizer.tokenize(sent) for sent in sentences]

    # 입력 토큰의 최대 시퀀스 길이
    MAX_LEN = 128

    # 토큰을 숫자 인덱스로 변환
    input_ids = [tokenizer.convert_tokens_to_ids(x) for x in tokenized_texts]
    
    # 문장을 MAX_LEN 길이에 맞게 자르고, 모자란 부분을 패딩 0으로 채움
    input_ids = pad_sequences(input_ids, maxlen=MAX_LEN, dtype="long", truncating="post", padding="post")

    # 어텐션 마스크 초기화
    attention_masks = []

    # 어텐션 마스크를 패딩이 아니면 1, 패딩이면 0으로 설정
    # 패딩 부분은 BERT 모델에서 어텐션을 수행하지 않아 속도 향상
    for seq in input_ids:
        seq_mask = [float(i>0) for i in seq]
        attention_masks.append(seq_mask)

    # 데이터를 파이토치의 텐서로 변환
    inputs = torch.tensor(input_ids)
    masks = torch.tensor(attention_masks)

    return inputs, masks

# 문장 테스트
def test_sentences(sentences):

    # 평가모드로 변경
    model1.eval()

    # 문장을 입력 데이터로 변환
    inputs, masks = convert_input_data(sentences)

    # 데이터를 GPU에 넣음
    b_input_ids = inputs.to(device)
    b_input_mask = masks.to(device)
            
    # 그래디언트 계산 안함
    with torch.no_grad():     
        # Forward 수행
        outputs = model1(b_input_ids, 
                        token_type_ids=None, 
                        attention_mask=b_input_mask)

    # 출력 로짓 구함
    logits = outputs[0]

    # CPU로 데이터 이동
    logits = logits.detach().cpu().numpy()

    return logits

tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased', do_lower_case=False)

# When I'm in a good mood.
good= ["Grilled Ribs", "Yukhoe", "Steamed Ribs", "Grilled Ribs", "Grilled Tripe", "Grilled Tripe Hot Pot"]
# When I'm depressed - fish + sweet food
depressed=['Cold Raw Fish', 'Grilled Pollack', 'Grilled Eel', 'Grilled Chopper', 'Grilled Shellfish', 'Seaweed Soup', 'Fried Squid', 'Fried Shrimp'
, "Seaweed", "Sannakji", "Seasoned raw octopus", "Seaweed", "Shrimp fried rice", "Stir-fried webfoot octopus", "Seasoned crab", "Fish pancake", "Steamed pollack",
"Braised saury," "Dongtae-jjigae," "Steamed seafood," "Seasoned chicken," "Jajangmyeon," "Jjolmyeon," "Kongguksu," "Rice balls," "Japchae."
, "Yubu Sushi", "Rice Skewers", "Pumpkin Jeon", "Soy sauce marinated crab", "Grilled hairtail", "Grilled mackerel", "Steamed mackerel", "Gwamegi"]
# When I'm stressed out - spicy food, cold food.
stressful=['grilled pollack', 'spicy stir-fried chicken', 'spicy stew', 'jjolmyeon', 'yukgaejang', 'bibim naengmyeon', 'sushi salad', 'skirt salad', 'tofu kimchi'
"Stir-fried spicy pork", "Stir-fried webfoot octopus", "Tteokbokki", "Rapokki", "Seasoned crab", "Stir-fried chicken", "Steamed pollack", "Dong7tae jjigae", "Steamed seafood",
"Cold Noodles", "Kongguksu", "Boiled Potatoes", "Fried Chili", "Kimchi Pancake"]




# 문장 생성 페이지
# ~/main/bert
@main.route('/bert', methods=['GET','POST'])
def bert():
    return render_template('bert.html')

@main.route('/res', methods=['GET','POST'])
def res():
    if request.method == 'POST':
        text = request.form.get('text')

        logits = test_sentences([text])

        if np.argmax(logits) == 0: # 만약에 분류감정이 sad면
            select_food = random.choice(depressed)
            sentence = f'You look sad.\n"{select_food}" is the best when you are depressed.' 
        elif np.argmax(logits) == 1: # 만약에 분류감정이 happy면
            select_food = random.choice(good)
            sentence = f'You must be in a good mood. Hoho!\nI recommend you to eat when you feel good!\nMy choice is "{select_food}"!!'
        elif np.argmax(logits) == 2: # 만약에 분류감정이 stress면
            select_food = random.choice(stressful)
            sentence = f'You look stressed!\n"{select_food}" is the best when you are stressed.'

        return sentence