# -*- coding: cp1251 -*-

from pony.thirdparty import sqlite
from pony.main import *
from pony.web import HttpRedirect

use_autoreload()

manager = False

def connect():
    return sqlite.connect('dbase.sqlite')

def interface(title=u'������ ����������'):
    return html( u'''<title>$title</title>
    <body BGCOLOR="#E7E3E7">
    <font color="#777777"><h1>$title</h1></font>
     ''')

@http('/')
@printhtml
def managerindex():
    print u'<body BGCOLOR="#E7E3E7">'
    print u"<h1>ERROR 403: forbidden</h1>"

@http('/management')
@printhtml
def managerlogin():
    global manager
    f=open(u"C:\\passwd")
    sp=f.readlines()
    print u'<body BGCOLOR="#E7E3E7">'
    fpass = Form()
    fpass.passwd = Password(u"������", required=True)
    if not fpass.is_valid:
        print u"<h2>������� ������ ���������:</h2>"
        print fpass
    else:
        if fpass.passwd.value+'\n' in sp:
            print u'�� - ��������!<br><br>'
            print link(control)
            manager = True
        else:
            print u'�� �������?<br><br>'
            manager = False
            print link(u'� ���������� � ������ :(',managerlogin)

@http('/management/control_panel')
@printhtml
def control():
    u"������ ����������"
    global manager
    if not manager: raise http.Redirect('/')
    print interface()
    print link(view)
    print '<br>'
    print link(books)

@http('/management/control_panel/view_orders')
@printhtml
def view():
    u'�������� � ������������� �������'
    global manager
    if not manager: raise http.Redirect('/')
    print interface(u'���������� ����������� ��������')
    con=connect()
    if con.execute(u'select id_������� from �����_�������').fetchone() is None:
        print u'������ �����������<br>'
        return
    clients = con.execute(u'select �����_������_�������, id_������� from �����_�������')
    passed_clients = set()
    for n_order, client_id in clients:
        if client_id in passed_clients: continue
        else: passed_clients.add(client_id)
        name, surname = con.execute(u'select ���, ������� from ������ where id=?',[client_id]).fetchone()
        print u'<hr><hr><br><strong>������:</strong> ', name, surname
        cursor = con.execute(u'select �����_������_�������, ����_������_�������, �������������, ��������� from �����_������� where id_�������=?',[client_id])
        for zak_id, date, yes, state in cursor:
            print html(u'''<hr><h3>����� ������: $date</h3>
                $if(yes==1){
                    $if(state==0){����� �����������<br>$link(done,zak_id)}
                    $else{����� ��������}}
                $else{$link(forward,zak_id)}<br><br><strong>���������� ������:</strong><br>''')
            cursor2 = con.execute(u'select �����_�����, ����������_�_������_������� from �����_�_������_������� where �����_������_�������=?', [ zak_id ] )
            for book_id, n_books in cursor2:
                cursor3 = con.execute(u'select ��������, ����� from ����� where id = ?', [book_id]).fetchone()
                name, author = cursor3
                print html(u'$author <strong>&quot;$name&quot;</strong> ($n_books ����)<br>')
    manager = False

@http('/management/control_panel/forward_order?id=$order_id')
@printhtml
def forward(order_id):
    u"��������� ����� ���������� � ����������� ���������� �����"
    print interface(u'����� ��������� � �����������')
    order_id=int(order_id)
    con = connect()
    cursor = con.execute(u'select �����_�����, ����������_�_������_������� from �����_�_������_������� where �����_������_������� = ?', [ order_id ] )
    for book_id, n_books in cursor:
        postavshik = con.execute(u'select ������������ from ����� where id = ?',[book_id]).fetchone()
        postavshik=str(postavshik)
        cursor2 = con.execute(u"insert into �����_���������� (���, ����_������_����������) values(?, datetime('now', 'localtime'))", [ postavshik ] )
        zakaz_id = cursor2.lastrowid
        cursor3 = con.execute(u"insert into �����_�_������_���������� (�����_�����, �����_������_����������, ����������_�_������_����������) values(?, ?, ?)",[book_id, zakaz_id, n_books])
    con.execute(u'update �����_������� set ������������� = 1 where �����_������_������� = ?',[order_id])
    con.commit()
    print u'����� ������� ������������� ����������� � �����������!'


@http('/management/control_panel/order_done?id=$order_id')
@printhtml
def done(order_id):
    u"�������� �����������"
    order_id=int(order_id)
    print interface(u'����� �������� �����������')
    con = connect()
    con.execute(u'update �����_������� set ��������� = 1 where �����_������_������� = ?',[order_id])
    con.commit()
    print u'����� ������� �������� �����������! �� ���� ��� ����� �������� �� �������� ��������� ������'

class BookForm(Form):
    def __init__(self):
        categories = []
        con = connect()
        cursor = con.execute(u'select �������� from ���������')
        for cat in cursor:
            cat = u'%s' %cat
            categories.append(cat)
        self.ISBN = Text(required=True)
        self.title = Text(u"��������", required=True)
        self.author = Text(u"�����", required=True)
        self.year = Text(u"���", required=True)
        self.publisher = Text(u"������������")
        self.image = File(u"��������")
        self.price = Text(u"����", required=True)
        self.cover = Text(u"��������")
        self.pages = Text(u"���������� �������")
        self.description = TextArea(u"���������", rows=10, cols=50, required=True)
        self.category = Select(u"���������",required=True,options=categories)
    def on_submit(self):
        if self.image.value: image = buffer(f.image.value.read())
        else: image = None
        con = connect()
        cursor = con.execute(u'insert into �����(ISBN, ��������, �����, ���_�������, ������������, �������, ����, ��������, ����������_�������, ���������, ���������)'
                             'values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                             [self.ISBN.value, self.title.value, self.author.value, self.year.value, self.publisher.value, image, self.price.value, self.cover.value,
                              self.pages.value, self.description.value, self.category.value])
        con.execute(u'update ����� set ���������_�����=random()')
        con.commit()

@http('/management/control_panel/add_books')
@printhtml
def books():
    u'���������� ����'
    print interface(u'���������� �������')
    global manager
    if not manager: raise http.Redirect('/')
    f = BookForm()
    print f
    manager = False

start_http_server('10.15.45.177:8081')

import webbrowser
webbrowser.open('http://10.15.45.177:8081/management/')