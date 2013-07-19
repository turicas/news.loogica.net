# -*- coding: utf-8 -*-
import re
import urllib2
from datetime import datetime, timedelta

from coopy.base import init_persistent_system
from werkzeug.contrib.atom import AtomFeed
from flask import Flask, request, redirect, render_template, jsonify, url_for

from domain import Item, News

import logging
log = logging.getLogger(__name__)

app = Flask(__name__)
news = init_persistent_system(News('main'))

@app.route('/')
def main():
    return render_template('loogica-news.html')

@app.route('/api/news')
def news_api():
    return jsonify(items=news.get_items())

@app.route('/api/vote/<item_id>')
def vote_api(item_id):
    item_id = int(item_id)
    news.vote(item_id)
    return jsonify(items=news.get_items())

@app.route('/api/remove/<item_id>')
def remove_api(item_id):
    item_id = int(item_id)
    news.remove(item_id)
    return jsonify(items=news.get_items())

@app.route('/api/post', methods=['POST'])
def add_api():
    link = request.form['link']
    try:
        data = urllib2.urlopen(link, timeout=10).read()
        title_search = re.search('<title>(.*)</title>', data, re.IGNORECASE)
        title = title_search.group(1)
        item = Item(title, link)
        news.add(item)
    except Exception as e:
        log.debug(e)
        return jsonify(error="Invalid Link or urlread timeout")
    return redirect(url_for('main'))

@app.route('/new')
def new():
    return render_template('new.html')

@app.route('/sobre')
def about():
    return render_template('about.html')

@app.route('/recent.atom')
def recent_feed():
    feed = AtomFeed('Loogica News',
                    feed_url=request.url,
                    url=request.url_root)
    items = news.get_items()
    for item in items:
        try:
            feed.add(title = item['title'].decode('utf-8'),
                     updated = datetime.strptime(item['posted'],
                                                   '%Y-%m-%d %H:%M:%S'),
                     url = item['link'])
        except Exception as e:
            log.debug("ewurror {0} {1}".format(e, item['title'].encode('utf-8')))

    return feed.get_response()

application = app
if __name__ == "__main__":
    app.run(debug=True)
