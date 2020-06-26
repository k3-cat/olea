from flask import g
from flask_json import json_response

from olea.auth import allow_anonymous

from . import bp
from .forms import ForgetPwd, Login, Refresh, ResetPwd, SetPwd, VEmail
from .services import LemonMgr, PinkMgr


@bp.route('/login', methods=['POST'])
@allow_anonymous
def login():
    form = Login()
    lemon = LemonMgr.grante(name=form.name, pwd=form.pwd, device_id=form.device_id)
    return json_response(id=lemon.id, key=lemon.key, exp=lemon.expiration)


@bp.route('/set-pwd', methods=['POST'])
def set_pwd():
    form = SetPwd()
    PinkMgr(g.pink_id).set_pwd(form.pwd)
    return json_response()


@bp.route('/forget-pwd', methods=['POST'])
@allow_anonymous
def reset_pwd_i():
    form = ForgetPwd()
    PinkMgr.forget_pwd(name=form.name, email=form.email)
    return json_response()


@bp.route('/reset-pwd', methods=['POST'])
@allow_anonymous
def reset_pwd():
    form = ResetPwd()
    PinkMgr.reset_pwd(token=form.token, pwd=form.pwd)
    return json_response()


@bp.route('/email-verification', methods=['POST'])
@allow_anonymous
def email_verification():
    form = VEmail()
    PinkMgr.verify_email(email=form.email)
    return json_response()


@bp.route('/refresh', methods=['POST'])
@allow_anonymous
def refresh():
    form = Refresh()
    token, exp = LemonMgr(form.id).grante_access_token(key=form.key, device_id=form.device_id)
    return json_response(token=token, exp=exp)


@bp.route('/lemons/', methods=['GET'])
def lemons():
    lemons = PinkMgr(g.pink_id).all_lemons()
    return json_response(data_=lemons)


@bp.route('/<id_>/revoke-lemon', methods=['POST'])
def revoke_lemon(id_):
    LemonMgr(id_).revoke()
    return json_response()


@bp.route('/revoke-all-lemons', methods=['POST'])
def revoke_all_lemons():
    LemonMgr.revoke_all()
    return json_response()
