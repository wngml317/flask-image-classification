from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
import mysql.connector
from mysql_connection import get_connection


class FollowResource(Resource) :
    
    @jwt_required()
    def post(self, follow_id) :

        # 1. 클라이언트로부터 데이터를 받아온다.
        user_id = get_jwt_identity()

        # 2. 데이터베이스에 친구정보 인서트한다.
        try :
            # 1) 디비에 연결
            connection = get_connection()

            # 2) 쿼리문 만들기
            query = '''insert into follow
                        (followerId, followeeId)
                        values
                        (%s, %s);'''
            
            record = (user_id, follow_id)

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
    def delete(self, follow_id) :
        
        user_id = get_jwt_identity()
        try :
            connection = get_connection()    

            query = '''delete from follow
                        where followerId = %s and followeeId=%s;'''
            record = (user_id, follow_id)

            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()

            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503
        return {'result' : 'success'}, 200

