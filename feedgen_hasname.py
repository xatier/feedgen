#!/usr/bin/env python3

import base36
import bottle
import feedgen.feed
import html
import json
import os
import requests
import urllib

app = application = bottle.Bottle()

@app.route('/')
def index():
    bottle.redirect('https://github.com/gslin/feedgen')

@app.route('/robots.txt')
def robotstxt():
    bottle.response.set_header('Content-Type', 'text/plain')
    return '#\nUser-agent: *\nDisallow: /\n'

@app.route('/pchome/<keyword>')
def pchome(keyword):
    url = 'https://ecshweb.pchome.com.tw/search/v3.3/all/results?q=%s&page=1&sort=new/dc' % (urllib.parse.quote_plus(keyword))

    title = 'PChome 搜尋 - %s' % (keyword)

    feed = feedgen.feed.FeedGenerator()
    feed.author({'name': 'Feed Generator'})
    feed.id(url)
    feed.link(href=url, rel='alternate')
    feed.title(title)

    r = requests.get(url);
    body = json.loads(r.text)

    for prod in body['prods']:
        # Product name & description
        prod_name = prod['name']
        prod_desc = prod['describe']
        prod_author = prod['author']

        # URL
        if prod['cateId'][0] == 'D':
            prod_url = 'https://24h.pchome.com.tw/prod/' + prod['Id']
        else:
            prod_url = 'https://mall.pchome.com.tw/prod/' + prod['Id']
        img_url = 'https://a.ecimg.tw%s' % (prod['picB'])

        body = '%s<br/><img alt="" src="%s"/>' % (html.escape(prod_desc), html.escape(img_url))

        entry = feed.add_entry()
        entry.author({'name': prod_author})
        entry.content(body, type='xhtml')
        entry.id(prod_url)
        entry.link(href=prod_url)
        entry.title(prod_name)

    bottle.response.set_header('Cache-Control', 'max-age=600,public')
    bottle.response.set_header('Content-Type', 'application/atom+xml')

    return feed.atom_str()

@app.route('/plurk/top/<lang>')
def plurktop(lang):
    url = 'https://www.plurk.com/Stats/topReplurks?period=day&lang=%s&limit=20' % (urllib.parse.quote_plus(lang))

    title = 'Plurk Top (%s)' % (lang)

    feed = feedgen.feed.FeedGenerator()
    feed.author({'name': 'Feed Generator'})
    feed.id(url)
    feed.link(href=url, rel='alternate')
    feed.title(title)

    r = requests.get(url)
    body = json.loads(r.text)

    for (x, stat) in body['stats']:
        url = 'https://www.plurk.com/p/' + base36.dumps(stat['id'])

        entry = feed.add_entry()
        entry.author({'name': stat['owner']['full_name']})
        entry.content(stat['content'], type='CDATA')
        entry.id(url)
        entry.link(href=url)
        entry.published(stat['posted'])
        entry.title(stat['content_raw'])

    bottle.response.set_header('Cache-Control', 'max-age=600,public')
    bottle.response.set_header('Content-Type', 'application/atom+xml')

    return feed.atom_str()

if __name__ == '__main__':
    if os.environ.get('PORT'):
        port = int(os.environ.get('PORT'))
    else:
        port = 8080

    bottle.run(app=app, host='0.0.0.0', port=port)
