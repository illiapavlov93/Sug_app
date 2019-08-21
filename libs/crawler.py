from libs.rabbit import RabbitManager
import queue
from models import db, Keywords
import requests
from init_app import create_app
import html
from threading import Thread

app = create_app()

def write_to_db(suggestion):
    try:
        sug = Keywords(suggestion)
        db.session.add(sug)
        db.session.commit()
    except:
        db.session.rollback()


def suggester(req):
    suggestions = []
    site = 'https://www.google.com/complete/search?q={}&cp=7&client=psy-ab&xssi=t&gs_ri=gws-wiz&hl=ru-UA&authuser=0&pq=ededed&psi=U0dUXZDbEaOWjgaT1Zb4Dw.1565804373330&ei=U0dUXZDbEaOWjgaT1Zb4Dw&gs_mss=crwale'.format(
        req)
    r = requests.get(site)
    page = r.text
    phrases = [item[0] for item in eval(html.unescape(page.replace(")]}'", "")))[0]]
    for i in phrases:
        suggestions.append(i.replace("<b>", "").replace("<\\/b>", ""))
    for i in suggestions:
        try:
            write_to_db(i)
        except Exception as e0:
            print(e0)
    return suggestions

class Crawler():
    def __init__(self):
        self.rabbit_queue = RabbitManager()
        self.inner_queue = queue.Queue()

    def run(self):
        t1 = Thread(target=self.listener())
        t2 = Thread(target=self.fetch())
        t1.start()
        t2.start()
        while True:
            t1.join()
            t2.join()

    def listener(self):
        task = self.rabbit_queue.get()
        self.inner_queue.put(task)

    def fetch(self):
        res = None
        if self.inner_queue.qsize() > 0 and res != None:
            web_task = self.inner_queue.get_nowait()
            req = web_task.body.decode('cp1251')
            res = suggester(req)
        else:
            print('queue is empty')
        return res

    # def write_to_db(self, suggestion):
    #     try:
    #         sug = Keywords(suggestion)
    #         db.session.add(sug)
    #         db.session.commit()
    #     except:
    #         db.session.rollback()
    #
    # def suggester(self, req):
    #     suggestions = []
    #     site = 'https://www.google.com/complete/search?q={}&cp=7&client=psy-ab&xssi=t&gs_ri=gws-wiz&hl=ru-UA&authuser=0&pq=ededed&psi=U0dUXZDbEaOWjgaT1Zb4Dw.1565804373330&ei=U0dUXZDbEaOWjgaT1Zb4Dw&gs_mss=crwale'.format(
    #         req)
    #     r = requests.get(site)
    #     page = r.text
    #     phrases = [item[0] for item in eval(html.unescape(page.replace(")]}'", "")))[0]]
    #     for i in phrases:
    #         suggestions.append(i.replace("<b>", "").replace("<\\/b>", ""))
    #     for i in suggestions:
    #         try:
    #             write_to_db(i)
    #         except Exception as e0:
    #             print(e0)
    #     return suggestions


if __name__ == '__main__':
    cr = Crawler()
    rq = RabbitManager()

    t1 = Thread(target=rq.get())
    t2 = Thread(target=cr.run())

