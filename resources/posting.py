from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql.connector.errors import Error
import mysql.connector
from mysql_connection import get_connection
from datetime import datetime
from config import Config
import boto3

class PostingResource(Resource) :

    @jwt_required()
    def post(self) :
        # 1. 클라이언트로부터 데이터를 받아온다.
        # photo(file), content(text)

        user_id = get_jwt_identity()


        if 'photo' not in request.files :
            return {'error' : '파일을 업로드하세요'}, 400

        file = request.files['photo']
        content = request.form['content']

        # 2. S3에 파일 업로드
        # 파일명을 우리가 변경해 준다.
        # 파일명은 유니크하게 만들어야 한다.
        current_time = datetime.now()
        new_file_name = current_time.isoformat().replace(':','_') + '.jpg'

        # 유저가 올린 파일의 이름을 내가 만든 파일명으로 변경
        file.filename = new_file_name

        # S3 에 업로드 하면 된다.
        # AWS의 라이브러리를 사용해야 한다.
        # 이 파이썬 라이브러리가 boto3 라이브러리다
        # boto3 라이브러리 설치
        # pip install boto3
        s3 = boto3.client('s3', aws_access_key_id = Config.ACCESS_KEY, aws_secret_access_key = Config.SECRET_ACCESS)        

        try :
            s3.upload_fileobj(file, Config.S3_BUCKET, file.filename, 
                                ExtraArgs = {'ACL' : 'public-read', 'ContentType' : file.content_type})

        except Exception as e:
            return {'error' : str(e)}, 500

        # 3. DB에 저장
        try :
            # 1) DB에 연결
            connection = get_connection()

            # 2) 쿼리문 만들기
            query = '''insert into posting
                        (imgUrl, content, userId)
                        values
                        (%s, %s, %s);'''
            
            record = (new_file_name, content, user_id)

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

        # 4. object detection을 수행해서 레이블의 Name을 가져온다.
        client = boto3.client('rekognition', 'ap-northeast-2', 
                                aws_access_key_id = Config.ACCESS_KEY, 
                                aws_secret_access_key = Config.SECRET_ACCESS)
        response = client.detect_labels(Image = {'S3Object' : 
                                        {'Bucket' : Config.S3_BUCKET, 'Name' : new_file_name}},
                                        MaxLabels=5)

        # 5. 레이블의 Name을 가지고 태그를 만든다.

        return {'result' : 'success',
                'Labels' : response['Labels']}
    

class PostingInfoResource(Resource) :
    @jwt_required()
    def put(self, posting_id) :
        # 1. 클라이언트로부터 데이터를 받아온다.
        # photo(file), content(text)

        user_id = get_jwt_identity()


        if 'photo' not in request.files :
            return {'error' : '파일을 업로드하세요'}, 400

        file = request.files['photo']
        content = request.form['content']

        # 2. S3에 파일 업로드
        # 파일명을 우리가 변경해 준다.
        # 파일명은 유니크하게 만들어야 한다.
        current_time = datetime.now()
        new_file_name = current_time.isoformat().replace(':','_') + '.jpg'

        # 유저가 올린 파일의 이름을 내가 만든 파일명으로 변경
        file.filename = new_file_name

        # S3 에 업로드 하면 된다.
        # AWS의 라이브러리를 사용해야 한다.
        # 이 파이썬 라이브러리가 boto3 라이브러리다
        # boto3 라이브러리 설치
        # pip install boto3
        s3 = boto3.client('s3', aws_access_key_id = Config.ACCESS_KEY, aws_secret_access_key = Config.SECRET_ACCESS)        

        try :
            s3.upload_fileobj(file, Config.S3_BUCKET, file.filename, 
                                ExtraArgs = {'ACL' : 'public-read', 'ContentType' : file.content_type})

        except Exception as e:
            return {'error' : str(e)}, 500

        # 2. 디비 업데이트 실행코드
        try :
            # 1. DB에 연결
            connection = get_connection()

            # 2. 쿼리문 만들기
            query = '''update posting
                    set imgUrl = %s , content = %s
                    where id = %s and userId = %s;'''
            
            record = (new_file_name, content, posting_id, user_id)

            # 3. 커서를 가져온다.
            cursor = connection.cursor()

            # 4. 쿼리문을 커서를 이용해서 실행한다
            cursor.execute(query, record)

            # 5. 커넥션을 커밋해줘야 한다. => 디비에 영구적으로 반영하라는 뜻
            connection.commit()

            # 6. 자원 해제
            cursor.close()
            connection.close()

        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503

        client = boto3.client('rekognition', 'ap-northeast-2', 
                                aws_access_key_id = Config.ACCESS_KEY, 
                                aws_secret_access_key = Config.SECRET_ACCESS)
        response = client.detect_labels(Image = {'S3Object' : 
                                        {'Bucket' : Config.S3_BUCKET, 'Name' : new_file_name}},
                                        MaxLabels=5)

        # 5. 레이블의 Name을 가지고 태그를 만든다.

        return {'result' : 'success',
                'Labels' : response['Labels']}

    @jwt_required()
    def delete(self, posting_id) :

        user_id = get_jwt_identity()
        try :
            connection = get_connection()

            query = '''delete from memo
                    where id=%s and user_id = %s;'''

            record = (posting_id, user_id)

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

    