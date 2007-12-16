# -*- coding: cp1251 -*-

import re, urllib
#from lxml import etree
from BeautifulSoup import BeautifulSoup, NavigableString

from pysqlite2 import dbapi2 as sqlite
con = sqlite.connect('dbase.sqlite')

site = 'http://books.filosofia.ru/'

page = urllib.urlopen(site).read().decode('cp1251')
soup = BeautifulSoup(page)

links = [ link for link in soup.findAll('a') if link.get('href').startswith('default.asp?rp=') ]
categories = {}
for link in links:
    title = unicode(link.string)
    if '+' in title: continue
    categories[link.get('href')] = title

for href, category in categories.items():
    href = site + href

    try:
        print category, ':', href
        print
    except: category = u'Неизвестная категория'

    row = con.execute(u'select * from Категория where Название = ?', [category]).fetchone()
    if row is not None: continue

    con.execute(u'insert or ignore into Категория values(?)', [category])

    page = urllib.urlopen(href).read().decode('cp1251')
    soup = BeautifulSoup(page)

    hrefs = [ None ] + [ link.get('href') for link in soup.findAll('a', {'class' : 'page'}) ]

    for href in hrefs:
        if href is not None:
            href = site + href
            page = urllib.urlopen(href).read().decode('cp1251')
            soup = BeautifulSoup(page)
        hrefs = [ link.get('href') for link in soup.findAll('a') if link.get('href').startswith('book.asp?cod=') ]
        for href in hrefs:
            href = site + href
            page = urllib.urlopen(href).read().decode('cp1251')
            soup = BeautifulSoup(page)
            form = soup.find('form', action='zakaz.asp')
            try: tr = form.parent.parent
            except: continue

            try:
                image_src = tr.td.img['src']
                image = buffer(urllib.urlopen(image_src).read())
            except: image = None
            title = unicode(tr.b.string)
            authors = unicode(tr.font.contents[0]).strip()
            if ':' in authors: authors = authors.split(':')[1].strip()
            else: authors = None
            publisher = unicode(tr.font.contents[2]).split(':')[1]

            cover = year = pages = ISBN = None
            for x in tr.font.contents[4:]:
                if not isinstance(x, NavigableString): continue
                data = unicode(x).split(',')
                for item in data:
                    try:
                        key, value = item.split(':')
                        key = key.strip()
                        value = value.strip()
                        if key == u'\u041f\u0435\u0440\u0435\u043f\u043b\u0435\u0442': cover = value
                        elif key == u'\u0433\u043e\u0434 \u0438\u0437\u0434\u0430\u043d\u0438\u044f': year = value
                        elif key == u'\u0441\u0442\u0440\u0430\u043d\u0438\u0446': pages = value
                        elif key == u'ISBN': ISBN = value
                    except: pass

            price = unicode(tr.font.font.string).replace(',', '.')

            description = []
            for x in tr.div.contents:
                if isinstance(x, NavigableString): description.append(x)
                elif x.name == 'br': description.append('<br>\n')
            description = ''.join(description)

            try:
                print '\t', title
                print '\t', authors, '|', publisher, '|', cover, '|', year, '|', pages, '|', ISBN, '|', price
                print
            except: continue

            con.execute(u'insert into Книга(Категория, Название, Автор, Издательство, ISBN, Переплет, Год_издания, Количество_страниц, Цена, Аннотация, Обложка) '
                        'values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        [ category, title, authors, publisher, ISBN, cover, year, pages, price, description, image])
    con.commit()