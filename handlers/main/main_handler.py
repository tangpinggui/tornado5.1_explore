import tornado.ioloop
import tornado.web


class MainHandler(tornado.web.RequestHandler):
    """ 首页 """
    def get(self):
        self.render('index.html')


class ExploreHandler(tornado.web.RequestHandler):
    """ 发现页 """
    def get(self):
        self.render('explore.html')


class ALoneHandler(tornado.web.RequestHandler):
    """ 单独页 """
    def get(self, id):
        self.render('alone.html', id=id)