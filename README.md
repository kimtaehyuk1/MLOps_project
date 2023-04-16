# MLOps_project
🐬도커 컨테이너 환경_웹사이트 구축 및 모델 서빙_AWS 인프라 구성🐬

----------------


<img src="https://user-images.githubusercontent.com/67897827/232330159-1b7d1933-3bb8-419a-ba3c-e4d69d197df7.png" width="1000" height="600"/>



## 참고필기(수정하기)
- 깃에 올린게 전부의 내용은 아님(ai-project4-taehyuk-cloud9파일 참고), 참고 필수만 올렸음.
- 인스턴스 관련해 보안그룹 포트 열어주기
- 도커로 컨테이너환경 나눈이유 확실히 이해
- 인프라 구성쪽은 참고4 영상 보기
- agent1은 예측 수행해서 결과 다른 큐에 넘겨주고, agent2는 큐2만 바라보다 결과생기면 db저장
- db에서 읽어서 뿌려주는거는 maincontroller에 구성.


- docker-compose.yml 과 각 컨테이너 환경의 Dockerfile 유심히 보기
- docker-compose up -d로 한번에 수행( 돌렸을때 안되는거 docker logs 이미지명 으로 찍어보면서 해결)
- 웹 볼때는 인스턴스IP: 로 보기

### 참고하면 좋은거
- 디비 참조
- docker run -d -p 3306:3306 --name my_mariadb --env MARIADB_ROOT_PASSWORD=12341234 mariadb
- docker exec -it my_mariadb bash
- mysql -u root -p
- show ~~~ 
----------------------
## 발전사항
- 웹 구체화 시키기(로그인기능, 자체 꾸미기)
- 아직 그리진 않았지만 
- EC2분해(모델쪽,3Tier쪽 <- 다르게 EC2 성능 맞추기, 모델은 크니까 m5large, 3Tier는 기본) -> 멀티 머신은 쿠버네티스로 관리
- 두 EC2간의 연결은 RDS로 주고 받기

