# -*- coding: cp1251 -*-

from pony.thirdparty import sqlite
from pony.main import *
from pony.web import HttpRedirect
import sha

use_autoreload()

def connect():
    return sqlite.connect('dbase.sqlite')

def header(title=u'Вы находитесь на Книги-почтой.ru'):
    return html( u'''<title>$title</title>
    <LINK href="/static/text.css" type=text/css rel=stylesheet>
    <body bgcolor="#d3d3d3" topmargin="1" marginwidth="10" marginheight="10" vlink="#0000ff" text="#000000">
    <table width=100% border="0" cellpadding="1" cellspacing="1" bgcolor="#d3d3d3" >
    <tr>
        <td align="center"><a href="$url(index)"><img src="/static/logo.jpg" border=0></a></td>
    </tr>
    <tr>
        <td align="center" ><font color="#777777"><h1>$title</h1></font></td>
    </tr>
    </table>
    <table bgcolor="#ffff8f" width=100% border="1" cellpadding="1" cellspacing="3">
    <tr>
     ''')

def footer():
    return html(u'''
    </tr>
    </table>
    <table width=100% height="50" border="1" cellpadding="0" cellspacing="0" bgcolor="#d3d3d3">
    <tr>
        <td width="300"><img src="/static/python.jpg"></td><td align=center ><font size=4 color=green>Copyright 2007 Aksenov A. & Solovieva T.<font><p>Возврат <a href="/">на гл. страницу</a></td>
    </tr>
    </table>
    </body>
     ''')

def sidebar(cat_id=0, book_id=0):
    return html(u'''
    <td align="left" valign="top" width="300" bgcolor="#fff0ff">
    $login()
	  $categories(cat_id, book_id)
    </td>
    ''')

@printhtml
def login():
    user = get_user()
    if user is not None:
        print u'<h3>Вы вошли как:</h3>'
        print u'<p class="blink">%s</p>' % get_session()['login']
        print u'<p>%s</p>' % link(u'Выйти',logout)
        print u'<p>%s</p>' % link(view_basket)
        return
    print u'<h3 class="sm">Вход для зарегистрированных пользователей:</h3>'
    f = Form(name='login')
    f.login = Text(u'Логин*', size=15)
    f.password = Password(u'Пароль*', size=15)
    f.submit = Submit(u'Войти')
    if f.is_submitted:
        if not f.login.value: f.login.error_text = u'Укажите логин!'
        elif not f.password.value: f.password.error_text = u'Укажите пароль!'
        else:
            db = connect()
            row = db.execute(u'select id, Пароль from Клиент where Логин = ?', [ f.login.value ]).fetchone()
            if row is None: f.login.error_text = u'Неверный логин'
            else:
                user_id, password = row
                hash = sha.new(f.password.value).hexdigest()
                if password != hash:
                    f.password.error_text = u'Неверный пароль'
                else:
                    set_user(user_id)
                    session = get_session()
                    session['login'] = f.login.value
                    print u'<h3>Вы вошли как:</h3>'
                    print u'<p class="blink">%s</p>' % f.login.value
                    print u'<p>%s</p>' % link(u'Выйти',logout)
                    print u'<p>%s</p>' % link(view_basket)
                    return
    print f
    print u'Еще не зарегистрированы?<br>'
    print '<img src="/static/hi.gif"><br>'
    print link(u'Исправьте это!',register)
    
@http('/?p=$pn')
@printhtml
def index(pn=0):
    pn=int(pn)
    con = connect()
    cursor = con.execute(u'select id, ISBN, Название, Автор, Год_издания, Обложка from Книга '
                         u'order by Случайное_число limit 100 offset ?',[pn*100])
    print html(u'''
    $header()
    $sidebar()
    <td align="left" valign="top"><h1>Добро пожаловать в наш магазин!</h1>
    <h2>Ознакомьтесь с ассортиментом:</h2>
    <center>$pages(pn)</center>
    $for(book_id, ISBN, title, authors, year, image in cursor) {
    <h3>$link(html(title), bookinfo, book_id)</h3>
    $if(image is None){<div align=center><a href="$url(bookinfo, book_id)"><img src="/static/nocover.gif" width=100 height=100 border=0></a></div>}
    $else{<div align=center><a href="$url(bookinfo, book_id)"><img src="$url(bookimage, book_id)" border=0></a></div>}    
    $if(authors is None){<h4 class="s1">Нет автора</h4>}$else{<h4 class="s1">$authors</h4>}
    <strong>$year</strong><hr>}
       <center>$pages(pn)</center>
    </td>
 
    $footer()''')

@http('/?c=$cat_id&p=$pn')
def cat_index(cat_id, pn=0):
    cat_id = int(cat_id)
    pn = int(pn)
    con = connect()
    cat_name = con.execute(u'select Название from Категория where rowid=?', [ cat_id ]).fetchone()[0]
    cursor = con.execute(u'select id, ISBN, Название, Автор, Год_издания, Обложка, Аннотация from Книга where Категория=? order by Случайное_число limit 20 offset ?',
                         [ cat_name, pn*20 ])
    return html(u'''
    $header($cat_name)
    $sidebar($cat_id)
    <td valign=top>
    <br>
    <center>$pages(pn, cat_id)</center>
    $for(book_id, ISBN, title, authors, year, image, description in cursor) {
    <h3>$link(html(title), bookinfo, book_id)</h3>
	$if(image is None){<div align=center><a href="http://localhost:8080$url(bookinfo, book_id)"><img src="/static/nocover.gif" width=100 height=100 border=0></a></div>}
	$else{<div align=center><a href="$url(bookinfo, book_id)"><img src="$url(bookimage, book_id)" border=0></a></div>}    
    $if(authors is None){<h4 class="s1">Нет автора</h4>}$else{<h4 class="s1">$authors</h4>}
    <strong>$year</strong><hr>}   
    <center>$pages(pn, cat_id)</center>
    </td>
    $footer()''')    

@http('/register')
@printhtml
def register():
    print header(u'Регистрация')
    f=Form()
    f.country = Select('Select your country',required=True,options=['','USA','Australia','Russia'])
    f.ok=Submit(value=u'Далее')
    if f.country.value in ('USA','Australia'):
        f.secure = True
        f.state = Select('Select your state', True)
        if f.country.value == 'USA':
            f.state.options = [ '', 'Alabama', 'New York', 'Virginia' ]
        else:
            f.state.options = [ '', 'Tasmania', 'Victoria', 'Western Australia']
        f.zip = Text('Zip code', required=True)
        f.first_name = Text(required=True)
        f.last_name = Text()
        f.email = Text('E-mail', required=True)
        f.password = Password(required=True)
        f.password2 = Password('Re-type password', True)
        f.comment = TextArea('You can type your comment here')
        f.file = File('Attachment file')
        f.subscribe = Checkbox('I want to receive the following news:', value=True)
        f.news_categories = MultiSelect(options=[ 'Daily reviews','Weekly digests','Security updates' ],
                                        value=[ 'Daily reviews','Weekly digests' ])
    elif f.country.value == 'Russia':
        f.secure = True
        f.country.label = u'Выберите страну'
        f.city = Select(u'Выберите город', True,options = ['', u'Москва',u'Санкт-Петербург', u'Владивосток'])
        f.last_name = Text(u'Фамилия', required=True)
        f.first_name = Text(u'Имя', required=True)
        f.patronymic_name = Text(u'Отчество')
        f.sex = RadioGroup(u'Пол', options=[ u'Мужской', u'Женский' ])
        f.email = Text(u'Почтовый адрес', True)
        f.login=Text(u'<b>Логин</b>',required=True)
        f.password = Password(u'Пароль', True)
        f.password2 = Password(u'Введите пароль еще раз', True)
        f.subscribe = Checkbox(u'Я хочу получать новости', value=True)
        f.news_categories = CheckboxGroup(u'Категории новостей',options=[(1,u'Недельные выпуски'),(2,u'Месячные выпуски'),(3,u'Срочные сообщения')],
                                          value=[ 1, 2 ])

    if (f.country.value and f.password.is_submitted
                        and f.password2.is_submitted
                        and f.password.value!=f.password2.value):
        if f.country.value == 'Russia': msg = u'Пароли не совпадаЮт!'
        else: msg = 'Passwords do not match!'
        f.password.error_text = f.password2.error_text = msg
    if f.is_valid:
        ok = True
        con = connect()
        row = con.execute(u'select id from Клиент where Логин = ?', [ f.login.value ]).fetchone()
        if row is not None:
            f.login.error_text = u'Такой логин уже занят'
            ok = False
        if ok:
            hash = sha.new(f.password.value).hexdigest()
            cursor = con.execute(u'insert into Клиент(Логин, Пароль, Имя, Фамилия, email) values(?, ?, ?, ?, ?)',
                                 [ f.login.value, hash, f.first_name.value, f.last_name.value, f.email.value ])
            user_id = cursor.lastrowid
            set_user(user_id)
            get_session()['login'] = f.login.value
            con.commit()
            raise HttpRedirect(url(register2))
    print u"Заполните необходимые регистрационные данные:"
    print f
    print footer()

@printhtml
def pages(pn, cat_id=None):
    con = connect()
    if cat_id is None:
        nbooks = con.execute(u'select count(*) from Книга ').fetchone()[0]
        if nbooks<21:return
        npages = (nbooks / 100) + 1
        for i in range(1, npages+1):
            if i == (pn+1): print '<strong>[%d]</strong>' % i
            else: print '[%s] ' % link(str(i), index, i-1)
    else:
        cat_name = con.execute(u'select Название from Категория where rowid=?', [cat_id]).fetchone()[0]
        nbooks = con.execute(u'select count(*) from Книга where Категория=?', [cat_name]).fetchone()[0]
        if nbooks<21:return
        npages = (nbooks / 20) + 1
        for i in range(1, npages+1):
            if i == (pn+1): print '<strong>[%d]</strong>' % i
            else: print '[%s] ' % link(str(i), cat_index, cat_id, i-1)
    print '<hr>'            

@http
@printhtml
def register2():
    login=get_session()['login']
    print header(u"Добро пожаловать, %s" % login)
    print u'<center><h1>Поздравляем, %s!</h1></center>' %login
    print u'<center><h2>Вы успешно зарегистрированы!</h2></center>'
    print footer()    

@http('/logout')
@printhtml
def logout():
    print header(u"Выход")
    print u'<body BGCOLOR="#E7E3E7">'
    user = get_session()['login']
    set_user(None)
    print html(u"""$if (user) { <h1>До встречи, $user!</h1>}
                <h2>Вы вышли</h2>""")
    print footer()

@http('/books/$book_id')
def bookinfo(book_id):
    con = connect()
    row = con.execute(u'select ISBN, Название, Автор, Год_издания, Издательство, Обложка, Аннотация, Категория, Цена, Переплет from Книга where id = ?', [book_id]).fetchone()
    if row is None: raise Http404
    ISBN, title, author, year, pub, image, description, cat, price, cover = row
    return html(u'''$header(u'Информация о книге "%s"' % html(title))
    $sidebar()
    <td valign=top>
    $if(image is None){<img src="/static/nocover.gif" width=100 height=100>}
    $else{<img src="$url(bookimage, book_id)">}    
    <p>$if(author is None){Нет автора}$else{<h4>$author</h4>}<br>
    <strong>$year</strong>
    <p><strong>Аннотация:</strong>
    <div class="description">$html(description)</div><br>
    <strong>Переплет: </strong>$if(cover is None){нет сведений}$else{$cover}<br>
    <strong>Цена: </strong>$if(price is None){договорная}$else{$price р.}<br>
    <strong>ISBN: </strong>$if(ISBN is None){отсутствует}$else{$ISBN}<br>
    <strong>Категория: </strong>$if(cat is None){нет}$else{$cat}<br>
    <strong>Издательство: </strong>$if(pub is None){нет}$else{$pub}<br>    
    $basket(book_id)
    <td>
    $footer()''')

@http('/images/books/$book_id', type='image/jpg')
def bookimage(book_id):
    con = connect()
    row = con.execute(u'select Обложка from Книга where id = ?', [ book_id ]).fetchone()
    if row is None: raise Http404
    return str(row[0])

class FormaDobavit(Form):
    def __init__(self, book_id):
        self.book_id = book_id
        self.submit = Submit(u'Добавить в корзину')
    def on_submit(self):
        http.session.setdefault('basket', set()).add(int(self.book_id))

class FormaUdalit(Form):
    def __init__(self, book_id):
        self.book_id = book_id
        self.submit = Submit(u'Удалить из корзины')
    def on_submit(self):
        http.session.setdefault('basket', set()).discard(int(self.book_id))

@printhtml
def categories(current_cat_id, current_book_id):
    print u'<h3 class="sm"></h3>'    
    print u'<hr><p><h3 class="sm">Выберите категорию:</h3><hr>'
    if current_cat_id == 0 and current_book_id == 0:
          print u'<p>Все категории'
    else: print u'<p>%s' % link(u'Все категории', index)
    print '<hr>'
    con = connect()
    for [cat_id, cat_name] in con.execute(u'Select rowid, Название from Категория'):
        if cat_id == current_cat_id: print '<p>%s' % cat_name
        else: print '<p>%s' % link(cat_name, cat_index, cat_id)
        print '<hr>'
	
@printhtml
def basket(book_id):
    user_id = get_user()
    if user_id is None:
        print u'<p>У Вас не будет корзины, пока Вы не зарегистрируетесь'
        return
    book_id = int(book_id)
    basket = http.session.setdefault('basket', set())
    if book_id not in basket:
        print u'<p>Вы можете добавить эту книгу в вашу личнуЮ корзину<br>'
        f = FormaDobavit(book_id)
    else:
        print u'<p>Книга находится в вашей личной корзине вы можете '
        f = FormaUdalit(book_id)
    print f
    
@http('/basket')
def view_basket():
    u"Ваша корзина"
    basket=http.session.get('basket', set())
    con = connect()
    cursor = con.execute(u'select id, ISBN, Название, Автор, Год_издания, Обложка from Книга where id in (%s)'
                         % ','.join(map(str, basket)))
    print html(u'''
    $header(u'Корзина')
    $sidebar()
    <td align="left" valign="top"><h1>Просмотр корзины</h1>
    $if(basket==set([])){Ваша корзина пока что пуста. Заполните ее понравившимися Вам книгами! :)
    <br>$link(u'На главнуЮ',index)}
    $else{
    $for(book_id, ISBN, title, authors, year, image in cursor) {
    <h3>$link(html(title), bookinfo, book_id)</h3>
    $if(image is None){<div align=center><a href="$url(bookinfo, book_id)"><img src="/static/nocover.gif" width=100 height=100 border=0></a></div>}
    $else{<div align=center><a href="$url(bookinfo, book_id)"><img src="$url(bookimage, book_id)" border=0></a></div>}    
    $if(authors is None){<h4 class="s1">Нет автора</h4>}$else{<h4 class="s1">$authors</h4>}
    <strong>$year</strong><hr>}
    $link(u'Отправить заказ',zakaz)}
    </td>
    $footer()''')

class ZakazForm(Form):
    def __init__(self):
        con=connect()
        basket=http.session.get('basket', set())
        cursor = con.execute(u'select id, Название, Автор from Книга where id in (%s)' % ','.join(map(str, basket)))
        for [book_id, name, author] in cursor:
            book_name=html('$author <strong>&quot;$name&quot;</strong>')
            setattr(self, 'item_%d' % book_id, Text(book_name, type=int, value=1))
    def on_submit(self):
        con=connect()
        basket=http.session.get('basket', set())
        cursor = con.execute(u"insert into Заказ_клиента(id_клиента, Дата_заказа_клиента, Подтверждение, Состояние) "
                             "values(?, datetime('now', 'localtime'), 0, 0)", [ http.user ])
        zakaz_id= cursor.lastrowid
        ok = False
        for book_id in basket:
            field = getattr(self, 'item_%d' % book_id, None)
            if field is None or not field.value: continue            
            print book_id, field.value
            con.execute(u"insert into Книга_в_заказе_клиента values(?, ?, ?)", [ zakaz_id, book_id, field.value ])
            ok = True
        if not ok: con.rollback()
        else: con.commit()
        basket.clear()
        raise http.Redirect('/')

@http('/zakaz')
@printhtml
def zakaz():
    f=ZakazForm()
    print html(u'''
    $header(u'Отправка заказа')
    $sidebar()
    <td align="left" valign="top"><h1>Уточните ваш заказ</h1>
    Введите количество экземпляров для каждой книги заказа! Если книга не нужна, вы можете ввести 0.
    $f
    </td>
    $footer()''')

@http('/moi_zakazi')
@printhtml
def view_zakazi():
    if http.user==None:raise http.Redirect('/')
    con=connect()
    print html(u'''
    $header(u'Ваши заказы')
    $sidebar()
    <td align="left" valign="top"><h1>Просмотр заказов</h1>''')
    print http.user
    cursor = con.execute(u'select Номер_заказа_клиента, Дата_заказа_клиента, Подтверждение, Состояние from Заказ_клиента where id_клиента=?',[http.user])
    for zak_id, date, yes, state in cursor:
        cursor2 = con.execute(u'select Номер_книги, Количество_в_заказе_клиента from Книга_в_заказе_клиента where Номер_заказа=?',[zak_id])
        print '!!!'
        for book_id, n_books in cursor2:
            cursor3 = con.execute(u'select Название, Автор from Книга where id = ?', [book_id])
            name,author = cursor3
            print '!!!'
            print html('''
            $for(zak_id, date, yes, state in cursor){
    <h3>Заказ сделан: $date</h3>
    $for(book_id, n_books in cursor2){$author <strong>&quot;$name&quot;</strong>')}
    $if(yes==1){
        $if(state==0){Заказ промотрен менеджером и находится в стадии выполнения...}
        $else{Заказ выполнен. Ждите книжки.}}
    $else{Заказ еще не обработан менеджерами.}
    <tr>
    }
    </td>
    $footer()''')

start_http_server('localhost:8080')

import webbrowser
webbrowser.open('http://localhost:8080/')
# show_gui()
