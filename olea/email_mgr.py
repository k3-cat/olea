from olea.exts import mailgun


def new_pink(email, name, pwd):
    mailgun.send(subject='初次见面, 这里是olea',
                 to=(email, ),
                 template='new_pink',
                 values={
                     'name': name,
                     'pwd': pwd
                 })


def reset_pwd(email, token):
    mailgun.send(subject='你的密码重置令牌', to=(email, ), template='reset_pwd', values={'token': token})
