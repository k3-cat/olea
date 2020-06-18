from olea.singleton import mailgun


def new_pink(email, name):
    mailgun.send(subject='初次见面, 这里是olea', to=(email, ), template='new_pink', values={'name': name})


def email_verification(email, token):
    mailgun.send(subject='邮箱确认',
                 to=(email, ),
                 template='email_verification',
                 values={'token': token})


def reset_pwd(email, token):
    mailgun.send(subject='你的密码重置令牌', to=(email, ), template='reset_pwd', values={'token': token})
