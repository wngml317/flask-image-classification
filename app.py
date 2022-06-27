from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from config import Config
from resources.follow import FollowResource
from resources.like import LikeResource
from resources.posting import PostingFollowResource, PostingInfoResource, PostingResource
from resources.tag import TagSearchResource
from resources.user import UserLoginResource, UserLogoutResource, UserRegisterResource

app = Flask(__name__)

# 환경변수 세팅
app.config.from_object(Config)

# JWT 토큰 라이브러리 만들기
jwt = JWTManager(app)

api = Api(app)

api.add_resource(UserRegisterResource, '/users/register')
api.add_resource(UserLoginResource, '/users/login')
api.add_resource(UserLogoutResource, '/users/logout')

api.add_resource(TagSearchResource, '/posting/search/tag')
api.add_resource(PostingResource, '/posting')
api.add_resource(PostingInfoResource, '/posting/<int:posting_id>')
api.add_resource(PostingFollowResource, '/posting/follow')

api.add_resource(FollowResource, '/follow/<follow_id>')
api.add_resource(LikeResource, '/like/<int:posting_id>')

if __name__ == '__main__' :
    app.run()