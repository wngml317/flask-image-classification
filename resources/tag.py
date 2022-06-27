from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
import mysql.connector
from mysql_connection import get_connection
from datetime import datetime
from config import Config
import boto3

class TagSearchResource(Resource) :
    def get(self) :
        
        # 1. 클라이언트로부터 데이터를 받아온다.
        keyword = request.args['keyword']
        offset = request.args['offset']
        limit = request.args['limit']

        # 2. 디비에서 해당 키워드가 들어있는 태그에 해당되는 
        # 포스팅 정보를 가져온다.

        try :
            connection = get_connection()

            query = '''select p.*
                        from tag_name tn
                        join tag t
                        on tn.id = t.tagId
                        join posting p
                        on p.id = t.postingId
                        where tn.name like '%{}%'
                        group by t.postingId
                        limit {}, {}'''.format(keyword, offset, limit)

            # select 문은 dictionary=True 를 해준다.
            cursor = connection.cursor(dictionary = True)

            cursor.execute(query)

            result_list = cursor.fetchall()
            print(result_list)

            # 중요! 디비에서 가져온 timestamp는
            # 파이썬의 datatime으로 자동 변경된다.
            # 문제는 ! 이제이터를 json으로 바로 보낼 수 없으므로 
            # 문자열로 바꿔서 다시 저장해서 보낸다.
            i = 0 
            for record in result_list :
                result_list[i]['createdAt'] = record['createdAt'].isoformat()
                result_list[i]['updatedAt'] = record['updatedAt'].isoformat()
                i = i + 1

            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return { "error" : str(e) }, 503

        return {'result' : 'success',
                'count' : len(result_list),
                'items' : result_list}