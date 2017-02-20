# coding: utf-8

import os
import json
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor

import tornado.ioloop
import tornado.web
from tornado.web import RequestHandler
from tornado import autoreload
from tornado.gen import coroutine


executor = ThreadPoolExecutor(max_workers=8)

def factorize(n):
    """ Функция разложения числа на множители """
    res = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            res.append(d)
            n //= d
        else:
            d += 1
    if n > 1:
        res.append(n)
    return res


class CalcHandler(RequestHandler):
    @coroutine
    def get(self):
        try:
            input_value = int(self.get_argument('n', None))
        except ValueError:
            self.set_status(400)
            self.write('please, provide an int')
            return
            
        out = yield executor.submit(factorize, input_value)
        res = {
            'in': self.get_argument('n', None),
            'out': out
        }
        self.set_header("Content-Type", 'application/json; charset="utf-8"')
        self.write(json.dumps(res, ensure_ascii=False))
        
    
class PageHandler(RequestHandler):
    """ Клиент """
    def get(self):
        self.render('main.html')


def make_app():
    CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
    TEMPLATE_PATH = os.path.join(CURRENT_PATH, 'templates')
    urls = [
        (r"/", PageHandler),
        ("/calc.json", CalcHandler),
    ]
    return tornado.web.Application(urls, template_path=TEMPLATE_PATH)

if __name__ == "__main__":
    app = make_app()
    app.listen(20100)
    autoreload.start()
    print('> server (re)started')
    tornado.ioloop.IOLoop.current().start()
    