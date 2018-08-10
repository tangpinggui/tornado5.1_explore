import tornado.web

from handlers.main import main_handler


application = tornado.web.Application([
        (r'/', main_handler.MainHandler),
    ])
