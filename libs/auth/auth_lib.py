from models.db.db_config import dbSession

from models.auth.model import User


def register_user_data(self, username, password1, password2):
    if not username:
        return {'status': False, 'message': '用户名不能为空'}
    if not password1 or not password2:
        return {'status': False, 'message': '密码不能为空'}
    if password1 != password2:
        return {'status': False, 'message': '两次密码不一致'}
    user = User.by_name(username)
    if user:
        return {'status': False, 'message': '用户名已存在'}
    user = User()
    user.name = username
    user.password = password1
    print(username, password1)
    print('--'*10)
    self.db.add(user)
    print('--'*10)
    self.db.commit()
    print('--'*10)

    return {'status': True, 'message': '注册成功'}


def login_auth(self, username, password):
    if not username:
        return {'status': False, 'message': '需要输入用户名'}
    if not password:
        return {'status': False, 'message': '需要输入密码'}
    user = User.by_name(name=username)
    if not user:
        return {'status': False, 'message': '该用户不存在'}
    if user.auth_password(password):
        return {'status': True, 'message': '登录成功'}


