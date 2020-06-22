from olea.singleton import mailgun


def new_pink(email, name):
    mailgun.send(subject='初次见面, 这里是olea', to=(email, ), template='new_pink', values={'name': name})


def email_verification(email, token):
    mailgun.send(subject='确认下邮箱. . 很快的. . .',
                 to=(email, ),
                 template='email_verification',
                 values={
                     'email': email,
                     'token': token
                 })


def pwd_reset(email, name, token):
    mailgun.send(subject='这是你刚下单的令牌 ~',
                 to=(email, ),
                 template='pwd_reset',
                 values={
                     'name': name,
                     'token': token
                 })
