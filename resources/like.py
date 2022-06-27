from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
import mysql.connector
from mysql_connection import get_connection

class LikeResource(Resource) :
    
    @jwt_required()
    def post(self, posting_id) :

        # 1. 클라이언트로부터 데이터를 받아온다.
        user_id = get_jwt_identity()

        # 2. 디비에 유저아이디와 포스팅아이디를 저장한다.
        try :
            # 1) 디비에 연결
            connection = get_connection()

            # 2) 쿼리문 만들기
            query = '''insert into likes
                        (userId, postingId)
                        values
                        (%s, %s);'''
            
            record = (user_id, posting_id)

            # 3) 커서를 가져온다.
            cursor = connection.cursor()

            # 4) 쿼리문을 커서를 이용하여 실행
            cursor.execute(query, record)

            # 5) 커넥션을 커밋해준다. -> 디비에 영구적으로 반영
            connection.commit()

            # 6) 자원 해제
            cursor.close()
            connection.close()
        
        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503

        return {"result" : "success"}

    @jwt_required()
    def delete(self, posting_id) :
        
        # 1. 클라이언트로부터 데이터를 받아온다.
        user_id = get_jwt_identity()

        # 2. 디비에 유저아이디와 포스팅아이디를 삭제한다.
        try :
            # 1) 디비에 연결
            connection = get_connection()

            # 2) 쿼리문 만들기
            query = '''delete from likes
                        where userId = %s and postingId=%s;'''
            record = (user_id, posting_id)

            # 3) 커서를 가져온다.
            cursor = connection.cursor()

            # 4) 쿼리문을 커서를 이용하여 실행
            cursor.execute(query, record)

            # 5) 커넥션을 커밋해준다. -> 디비에 영구적으로 반영
            connection.commit()

            # 6) 자원 해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503
        return {'result' : 'success'}, 200