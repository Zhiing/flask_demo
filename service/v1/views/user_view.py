from service import (db, logger)

from flask import request
from sqlalchemy import func, and_, or_
from flask_restful import Resource

from service.v1.permissions import verify_token
from service.common import (AccountRepeatException,
                            RequestParameterException)
from service.models import (DIDUserModel,
                            DIDGroupModel)
from service.models import (DICUserStatusModel,
                            DICGroupTypeModel,
                            DICGroupStatusModel)


class UserView(Resource):
    # @verify_token(request)
    def get(self):
        _user_id = request.args.get('id')

        try:
            user_query = db.session.query(DIDUserModel.id,
                                          DIDUserModel.passwd,
                                          DIDUserModel.phone,
                                          DIDUserModel.email,
                                          DIDUserModel.photo,
                                          DIDUserModel.group_id,
                                          DIDUserModel.status,
                                          DIDUserModel.ctime,
                                          DIDUserModel.mtime). \
                filter(DIDUserModel.id == _user_id).first()

            return {'user_id': user_query.id, 'password': user_query.passwd}
        except Exception as e:
            logger.error(e)
            raise e

    def post(self):
        _username = request.json.get('userName')
        _passwd = request.json.get('passWord')
        _phone = request.json.get('phoneNumber')
        _email = request.json.get('userEmail')
        _group_id = request.json.get('groupId')

        try:
            if None in (_username, _passwd, _phone, _email, _group_id):
                raise RequestParameterException

            user_query = db.session.query(DIDUserModel.id,
                                          DIDUserModel.phone,
                                          DIDUserModel.email). \
                filter(or_(DIDUserModel.phone == _phone,
                           DIDUserModel.email == _email)).first()
            if user_query is not None:
                if user_query.phone == _phone:
                    raise AccountRepeatException
                elif user_query.email == _email:
                    raise AccountRepeatException

            _user_data = DIDUserModel(
                uname=_username,
                _password=_passwd,
                phone=_phone,
                email=_email,
                group_id=_group_id)
            db.session.add(_user_data)
            db.session.commit()

            return {'code': 200, 'message': '添加成功'}
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            raise e
        