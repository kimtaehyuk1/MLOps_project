from flask import render_template, request, url_for, redirect, session
from service.controllers import bp_auth as auth

# ~/auth
@auth.route('/')
def home():
    # url_for( "별칭.함수명" ) => url이 리턴된다
    print( url_for('auth_bp.login') )
    return "auth 홈"

@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        # 1. uid, upw 획득
        uid = request.form.get('uid')
        upw = request.form.get('upw')
        session['uid']=uid
        # 2. uid, upw로 회원이 존재하는지 체크->(원래디비, 임시로값비교)
        if uid=='guest' and upw=='1234':
            return redirect( url_for('main_bp.home') )