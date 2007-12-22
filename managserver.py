# -*- coding: cp1251 -*-

from pony.thirdparty import sqlite
from pony.main import *
from pony.web import HttpRedirect

use_autoreload()

manager = False

def connect():
    return sqlite.connect('dbase.sqlite')

def interface(title=u'Панель управления'):
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
    fpass.passwd = Password(u"Пароль", required=True)
    if not fpass.is_valid:
        print u"<h2>Введите пароль менеджера:</h2>"
        print fpass
    else:
        if fpass.passwd.value+'\n' in sp:
            print u'Вы - менеджер!<br><br>'
            print link(control)
            manager = True
        else:
            print u'Мы знакомы?<br><br>'
            manager = False
            print link(u'Я опечатался в пароле :(',managerlogin)

@http('/management/control_panel')
@printhtml
def control():
    u"Панель управления"
    global manager
    if not manager: raise http.Redirect('/')
    print interface()
    print link(view)
    print '<br>'
    print link(books)

@http('/management/control_panel/view_orders')
@printhtml
def view():
    u'Просмотр и подтверждение заказов'
    global manager
    if not manager: raise http.Redirect('/')
    print interface(u'Управление клиентскими заказами')
    con=connect()
    if con.execute(u'select id_клиента from Заказ_клиента').fetchone() is None:
        print u'Заказы отсутствуЮт<br>'
        return
    clients = con.execute(u'select Номер_заказа_клиента, id_клиента from Заказ_клиента')
    passed_clients = set()
    for n_order, client_id in clients:
        if client_id in passed_clients: continue
        else: passed_clients.add(client_id)
        name, surname = con.execute(u'select Имя, Фамилия from Клиент where id=?',[client_id]).fetchone()
        print u'<hr><hr><br><strong>Клиент:</strong> ', name, surname
        cursor = con.execute(u'select Номер_заказа_клиента, Дата_заказа_клиента, Подтверждение, Состояние from Заказ_клиента where id_клиента=?',[client_id])
        for zak_id, date, yes, state in cursor:
            print html(u'''<hr><h3>Заказ сделан: $date</h3>
                $if(yes==1){
                    $if(state==0){Заказ подтвержден<br>$link(done,zak_id)}
                    $else{Заказ выполнен}}
                $else{$link(forward,zak_id)}<br><br><strong>Содержание заказа:</strong><br>''')
            cursor2 = con.execute(u'select Номер_книги, Количество_в_заказе_клиента from Книга_в_заказе_клиента where Номер_заказа_клиента=?', [ zak_id ] )
            for book_id, n_books in cursor2:
                cursor3 = con.execute(u'select Название, Автор from Книга where id = ?', [book_id]).fetchone()
                name, author = cursor3
                print html(u'$author <strong>&quot;$name&quot;</strong> ($n_books штук)<br>')
    manager = False

@http('/management/control_panel/forward_order?id=$order_id')
@printhtml
def forward(order_id):
    u"Отправить заказ поставщику и подтвердить клиентский заказ"
    print interface(u'Заказ отправлен и подтвержден')
    order_id=int(order_id)
    con = connect()
    cursor = con.execute(u'select Номер_книги, Количество_в_заказе_клиента from Книга_в_заказе_клиента where Номер_заказа_клиента = ?', [ order_id ] )
    for book_id, n_books in cursor:
        postavshik = con.execute(u'select Издательство from Книга where id = ?',[book_id]).fetchone()
        postavshik=str(postavshik)
        cursor2 = con.execute(u"insert into Заказ_поставщику (Имя, Дата_заказа_поставщику) values(?, datetime('now', 'localtime'))", [ postavshik ] )
        zakaz_id = cursor2.lastrowid
        cursor3 = con.execute(u"insert into Книга_в_заказе_поставщику (Номер_книги, Номер_заказа_поставщику, Количество_в_заказе_поставщику) values(?, ?, ?)",[book_id, zakaz_id, n_books])
    con.execute(u'update Заказ_клиента set Подтверждение = 1 where Номер_заказа_клиента = ?',[order_id])
    con.commit()
    print u'Заказ клиента перенаправлен поставщикам и подтвержден!'


@http('/management/control_panel/order_done?id=$order_id')
@printhtml
def done(order_id):
    u"Объявить выполненным"
    order_id=int(order_id)
    print interface(u'Заказ объявлен выполненным')
    con = connect()
    con.execute(u'update Заказ_клиента set Состояние = 1 where Номер_заказа_клиента = ?',[order_id])
    con.commit()
    print u'Заказ клиента объявлен выполненным! Об этом ему будет сообщено на странице состояния заказа'

class BookForm(Form):
    def __init__(self):
        categories = []
        con = connect()
        cursor = con.execute(u'select Название from Категория')
        for cat in cursor:
            cat = u'%s' %cat
            categories.append(cat)
        self.ISBN = Text(required=True)
        self.title = Text(u"Название", required=True)
        self.author = Text(u"Автор", required=True)
        self.year = Text(u"Год", required=True)
        self.publisher = Text(u"Издательство")
        self.image = File(u"Картинка")
        self.price = Text(u"Цена", required=True)
        self.cover = Text(u"Переплет")
        self.pages = Text(u"Количество страниц")
        self.description = TextArea(u"Аннотация", rows=10, cols=50, required=True)
        self.category = Select(u"Категория",required=True,options=categories)
    def on_submit(self):
        if self.image.value: image = buffer(f.image.value.read())
        else: image = None
        con = connect()
        cursor = con.execute(u'insert into Книга(ISBN, Название, Автор, Год_издания, Издательство, Обложка, Цена, Переплет, Количество_страниц, Аннотация, Категория)'
                             'values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                             [self.ISBN.value, self.title.value, self.author.value, self.year.value, self.publisher.value, image, self.price.value, self.cover.value,
                              self.pages.value, self.description.value, self.category.value])
        con.execute(u'update Книга set Случайное_число=random()')
        con.commit()

@http('/management/control_panel/add_books')
@printhtml
def books():
    u'Добавление книг'
    print interface(u'Управление книгами')
    global manager
    if not manager: raise http.Redirect('/')
    f = BookForm()
    print f
    manager = False

start_http_server('10.15.45.177:8081')

import webbrowser
webbrowser.open('http://10.15.45.177:8081/management/')