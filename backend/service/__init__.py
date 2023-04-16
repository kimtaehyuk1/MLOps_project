from flask import Flask


def create_app():
    app = Flask(__name__)

    app.secret_key='asdadada'
    
    # 블루프린트 초기화
    init_blueprint( app )   

    return app

def init_blueprint( app ):
    # 불루프린트로 정의된 개별 페이지 관련 내용 로드
    from .controllers import main_controller
    from .controllers import auth_controller
    
    from .controllers import bp_main, bp_auth

    # 플라스크 객체에 블루 프린트 등록
    app.register_blueprint(bp_main)
    app.register_blueprint(bp_auth)

    pass