import glob
import PIL.Image as Image
import uuid
import os

from models.auth.model import Posts, User
from models.db.db_config import dbSession


class MainFileLib(object):
    uploads_dir = 'uploads'
    thumbs_dir = 'thumbs'
    thumbs_size = [100, 100]

    def __init__(self, static_path, file_name):
        self.static_path = static_path
        self.upload_name = file_name
        self.file_name = self.uuid_file_name

    @property
    def uuid_file_name(self):
        ''' random file name '''
        uu = uuid.uuid4().hex
        _, ext = os.path.splitext(self.upload_name)
        return uu + ext

    @property
    def get_save_file_path(self):
        ''' get file to save path '''
        return os.path.join(self.static_path, self.uploads_dir, self.file_name)

    @property
    def get_upload_file_url(self):
        ''' get upload file url '''
        return os.path.join(self.uploads_dir, self.file_name)

    def save_file(self, content):
        ''' save file to 'get_save_file_path' '''
        with open(self.get_save_file_path, 'wb') as f:
            f.write(content)

    @property
    def get_thumbnail_file_path(self):
        ''' get thumbs file saved path '''
        file_name, ext = os.path.splitext(self.file_name)
        return os.path.join(self.static_path, self.uploads_dir, self.thumbs_dir, '{}_{}x{}{}'.format(
            file_name, self.thumbs_size[0], self.thumbs_size[1], ext
        ))

    def save_thumbs_file(self, content):
        ''' save thumbs to 'static/uploads/thumbs' '''
        img = Image.open(self.get_save_file_path)
        img.thumbnail(self.thumbs_size)
        img.save(self.get_thumbnail_file_path, 'JPEG')

    @property
    def get_upload_thumbs_url(self):
        ''' get thumbs url '''
        return self.get_thumbnail_file_path.split(self.static_path+'/')[1]

    def upload_file_and_thumbs_file(self, username):
        ''' upload file and it's thumbs file url to db '''
        posts = Posts(
            uploads_url=self.get_upload_file_url,
            thumbs_url=self.get_upload_thumbs_url,
            user_id=User.by_name(username).id,
        )
        dbSession.add(posts)
        dbSession.commit()


def get_all_images(path):
    os.chdir('static')  # 改变工作目录到 static
    fs = glob.glob(path + '/*.jpg')  # uploads/*.jpg
    os.chdir('..')  # 改变工作目录回到todo
    return fs


def save_files_lib(abs_img_path, img):
    ''' 存图片 '''
    try:
        with open(abs_img_path, 'wb') as f:
            f.write(img)
    except:
        return False
    return True


def change_to_thumbnail(img_save_path, abs_thumbnail_father_path):
    ''' 存缩略图 '''
    img = Image.open(img_save_path)
    size = (100, 100)
    img_name = os.path.basename(img_save_path)
    img_name_point_left, img_right = os.path.splitext(img_name)
    thumbnail_save_path = abs_thumbnail_father_path + img_name_point_left + '{}x{}'.format(size[0], size[1]) + img_right
    img.thumbnail(size)
    img.save(thumbnail_save_path, 'JPEG')
    return True
