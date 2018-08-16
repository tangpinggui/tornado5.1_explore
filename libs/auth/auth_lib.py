from models.db.db_config import dbSession

from models.auth.model import User, Posts, Like


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


def add_or_del_like(status, file_id, username):
    if not username:
        return {'code': 400, 'message': 'weidenglu'}
    user = User.by_name(name=username)
    user_id = user.id

    post = Posts.by_id(id=file_id)
    likes = post.like
    if likes:
        for like in likes:
            if like.user_id == user_id:
                if status:
                    like.like_num = 1
                else:
                    like.like_num = 0
            else:
                if status:
                    like = Like(
                        like_num=1,
                        post_id=file_id,
                        user_id=user_id
                    )
    else:
        like = Like(
            like_num=1,
            post_id=file_id,
            user_id=user_id
        )
    dbSession.add(like)
    dbSession.commit()
    return {'code': 200, 'message': '处理成功'}