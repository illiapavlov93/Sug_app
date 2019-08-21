from flask import request, render_template
from flask import current_app as app
from models import db, Keywords
import requests
import html


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


def check(search_for):
    if search_for:
        suggestions = db.session.query(Keywords).filter(
            Keywords.keyword.like('%' + search_for + '%')).all()
        if len(suggestions) < 5:
            suggestions = suggester(search_for)
    return suggestions


@app.route('/')
def base():
    return render_template('base.html')


@app.route('/', methods=['POST'])
def suggestion():
    search_for = Keywords(request.form['keyword'])
    suggestions = check(search_for.keyword)
    return render_template('suggestions.html',
                           keyword=search_for.keyword,
                           suggestions=suggestions,
                           pagination=False)
