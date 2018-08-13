import tornado.ioloop
import tornado.web
import uuid
import os

from libs import main_libs


class MainHandler(tornado.web.RequestHandler):
    """ 首页 """
    def get(self):
        urls = main_libs.get_all_images('thumbs')
        self.render('index.html', urls=urls)


class ExploreHandler(tornado.web.RequestHandler):
    """ 发现页 """
    def get(self):
        path = 'uploads'
        img_urls = main_libs.get_all_images(path)
        length = len(img_urls)
        self.render('explore.html', img_urls=img_urls, length=length)


class ALoneHandler(tornado.web.RequestHandler):
    """ 单独页 """
    def get(self, id):
        urls = main_libs.get_all_images('uploads')
        self.render('alone.html', url=urls[int(id)])


class UploadHandler(tornado.web.RequestHandler):
    """ 接收图片并储存,再储存一张缩略图 """
    def get(self, *args, **kwargs):
        self.render('upload.html')

    def post(self, *args, **kwargs):
        files = self.request.files.get('files')  # [{'filename': x, 'body': x..., 'content_type': 'image/jpeg'},]
        abs_img_father_path = 'static/uploads/'
        abs_thumbnail_father_path = 'static/thumbs/'
        if files:
            for file in files:
                uu = str(uuid.uuid1())
                img_save_name = uu + '_' + file['filename']
                img_save_path = abs_img_father_path + img_save_name
                result = main_libs.save_files_lib(img_save_path, file['body'])
                if result:
                    thumbnail_result = main_libs.change_to_thumbnail(img_save_path, abs_thumbnail_father_path)
                    return self.redirect('/explore')
        else:
            self.write('no any files')