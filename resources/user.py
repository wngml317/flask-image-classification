from flask import request
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
from flask_restful import Resource
from email_validator import validate_email, EmailNotValidError
from mysql.connector.errors import Error
import mysql.connector
from mysql_connection import get_connection
from utils import check_password, hash_password


class UserRegisterResource(Resource) :
    def post(self) :

        # 1. 클라이언트로부터 넘어온데이터를 받아온다.
        # {
        #     "email" : "aa@naver.com",
        #     "password" : "1234",
        #     "name" : "gildong"
        # }

        data = request.get_json()


        # 2. 이메일 주소 형식 체크

        try:
            validate_email(data['email'])

        except EmailNotValidError as e:
            # 이메일 형식이 유효하지 않으면, exception message 출력
            return { "error" : str(e), 'error_no' : 1}, 400

        # 3. 비밀번호의 길이가 유효한지 체크
        # 비밀번호 길이는 4자리 이상, 12자리 이하로만
        if len(data['password']) < 4 or len(data['password']) > 12 :
            return {"error" : "비밀번호 길이를 확인하세요", 'error_no' : 2}, 400

        # 4. 비밀번호 암호화
        hashed_password = hash_password(data['password'])
        print(hashed_password)

        # 5. 회원정보를 데이터베이스에 저장
        try :
            # 1) DB에 연결
            connection = get_connection()

            # 2) 쿼리문 만들기
            query = '''insert into user
                        (email, password, name)
                        values
                        (%s, %s, %s);'''
            record = (data['email'], hashed_password, data['name'])

            # 3) 커서를 가져온다.
            cursor = connection.cursor()

            # 4) 쿼리문을 커서를 이용하여 실행
            cursor.execute(query, record)

            # 5) 커넥션을 커밋해준다. -> 디비에 영구적으로 반영
            connection.commit()

            # 5-1) 디비에 저장된 아이디값 가져오기
            user_id = cursor.lastrowid

            # 6) 자원 해제
            cursor.close()
            connection.close()


        except mysql.connector.Error as e :
            print(e)
            cursor.close()

            connection.close()
            return {"error" : str(e), 'error_no' : 3}, 503

        # 6. access token을 생성해서 클라이언트에 응답해준다.
        # user_id 를 바로 보내면 안되고,
        # JWT로 암호화해서 보내준다.
        # 암호화하는 방법
        access_token = create_access_token(user_id)

        return {"result" : "success", 'access_token' : access_token},200

class UserLoginResource(Resource) :

    def post(self) :
        # {
        #     "email" : "aa@naver.com",
        #     "password" : "1234"
        # }

        data = request.get_json()

        try :
            connection = get_connection()

            query = '''select * 
                        from user
                        where email = %s'''
            
            record = (data['email'], )

            cursor = connection.cursor(dictionary = True)

            cursor.execute(query, record)

            result_list = cursor.fetchall()

            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503

        # 이메일 유효성 확인
        # 이 이메일의 유저가 없으면 
        # 클라이언트에 이 이메일은 회원이 아니라고 응답해준다.
        if len(result_list) != 1 :
            return {"error" : "회원가입이 안된 이메일입니다."}, 400

        # 비밀번호 확인

        # 디비에 저장되어 있는 유저 정보
        user_info = result_list[0]
        print(user_info)

        # data['password'] 와 user_info['password']를 비교
        check = check_password(data['password'], user_info['password'])
        
        if check == False :
            return {"error" : "비밀번호가 일치하지 않습니다."} 

        # JWT 억세스 토큰 생성해서 리턴해준다.
        access_token = create_access_token(user_info['id'])

        return {"result" : "success", "access_token" : access_token}, 200   


# 로그아웃 되었는지 확인해줌
# set에 토큰이 있으면 로그아웃한 유저
jwt_blacklist = set()

# 로그아웃 기능을 하는 클래스
class UserLogoutResource(Resource) :
    @jwt_required()
    def post(self) :
        
        # 헤더 부분에 jti를 가져와
        jti = get_jwt()['jti']
        print(jti)

        # jwt_blacklist에 jti 값을 넣어줌
        jwt_blacklist.add(jti)

        return {"result" : "success"}