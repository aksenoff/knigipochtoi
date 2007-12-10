# -*- coding: cp1251 -*-

from pony.thirdparty import sqlite
from pony.main import *

use_autoreload()

def connect():
    return sqlite.connect('dbase.sqlite')

def header(title=u'Книги-почтой'):
    return html( u'''<title>$title</title>
    <LINK href="text.css" type=text/css rel=stylesheet>
    <body bgcolor="#d3d3d3" topmargin="0" marginwidth="0" marginheight="0" vlink="#0000ff" text="#000000">
    <table width=100% border="0" cellpadding="0" cellspacing="0" bgcolor="#d3d3d3" >
    <tr>
        <td align="center">Здесь будет рисунок (может быть)</td>
    </tr>
    <tr><td align="center" >&nbsp;&nbsp;&nbsp;<font color="#778899"><h1>$title</h1></font></td></tr>
    </table>

    <table bgcolor="#fffff0" width=100% border="0" cellpadding="0" cellspacing="5">
    <tr>
     ''')

def footer():
    return html(u'''
    </tr>
    </table>

    <table width=100% height="50" border="0" cellpadding="0" cellspacing="0" bgcolor="#d3d3d3">
    <tr>
        <td align=center ><font size=4 color=green>Copyright 2007<font><p>Возврат <a href="/">на гл. страницу</a></td>
    </tr>
    </table>
    </body>
     ''')

def sidebar():
    return html(u'''
    <td align="center" valign="top" width="250" bgcolor="#d3d3d3">
       <h3 class="sm">Левая колонка</h3>
        $login_component()
        $if(get_session().get('is_manager')) { <p>$link(add_book)</p>  }
    </td>
    ''')

@printhtml
def login_component():
    user = get_user()
    if user is not None:
        print u'<h3>Пользователь:</h3>'
        print u'<p>%s</p>' % get_session()['login']
        print u'<p>%s</p>' % link(logout)
        return

    f = Form(name='login')
    f.login = Text(u'Логин', size=15)
    f.password = Password(u'Пароль', size=15)
    f.submit = Submit(u'Вход!')

    if f.is_submitted:
        if not f.login.value: f.login.error_text = u'Логин не задан'
        elif not f.password.value: f.password.error_text = u'Пароль не задан'
        else:
            db = connect()
            row = db.execute('select id, pass, is_manager from Users where login = ?', [ f.login.value ]).fetchone()
            if row is None: f.login.error_text = u'Неверный логин'
            else:
                user_id, password, is_manager = row
                hash = sha.new(f.password.value).hexdigest()
                if password != hash:
                    f.password.error_text = u'Неверный пароль'
                else:
                    set_user(user_id)
                    session = get_session()
                    session['login'] = f.login.value
                    session['is_manager'] = is_manager
                    print u'<h3>Текущий пользователь:</h3>'
                    print u'<p class="blink">%s</p>' % f.login.value
                    print u'<p>%s</p>' % link(logout)
                    return
    print f
    print link(register)
    
@http('/')
@printhtml
def index():
    print header()
    print sidebar()
    print u'<td><h2>Свежие поступления:</h2>'
    print u"<h1>Добро пожаловать в наш магазин!</h1>"
    print u'Выберите интересующее вас действие:</td>'
    print footer()

@http('/register')
@printhtml
def register():
    print header(u'Регистрация')
    print u'<body BGCOLOR="#E7E3E7">'
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
        f.comment = TextArea('You can type comment here')
        f.file = File('Attachment file')
        f.subscribe = Checkbox('I want receive news', value=True)
        f.news_categories = MultiSelect(options=[ 'Daily reviews','Weekly digests','Security updates' ],
                                        value=[ 'Daily reviews','Weekly digests' ])
    elif f.country.value == 'Russia':
        f.secure = True # Make multi-step form secure only on last step
        f.country.label = u'Выберите страну'
        f.city = Select(u'Выберите город', True,options = ['', u'Москва',u'Санкт-Петербург', u'Владивосток'])
        f.last_name = Text(u'Фамилия', required=True)
        f.fist_name = Text(u'Имя', required=True)
        f.patronymic_name = Text(u'Отчество')
        f.sex = RadioGroup(u'Пол', options=[ u'Мужской', u'Женский' ])
        f.email = Text(u'Почтовый адрес', True)
        f.password = Password(u'Пароль', True)
        f.password2 = Password(u'Введите пароль еще раз', True)
        f.subscribe = Checkbox(u'Я хочу получать новости', value=True)
        f.news_categories = CheckboxGroup(u'Категории новостей',options=[(1,u'Недельные выпуски'),(2,u'Месячные выпуски'),(3,u'Срочные сообщения')],
                                          value=[ 1, 2 ])

    if (f.country.value and f.password.is_submitted
                        and f.password2.is_submitted
                        and f.password.value != f.password2.value):
        if f.country.value == 'Russia': msg = u'Пароль не совпадает!'
        else: msg = 'Password did not match!'
        f.password.error_text = f.password2.error_text = msg
    print f.html
    print footer()

@http('/login?user=$user')
@printhtml
def login(user=None):
    print header(u"Вход")
    print u'<body BGCOLOR="#E7E3E7">'
    if user: set_user(user)
    session = get_session()
    session['x'] = 1
    print html(u"""$if (not user)
                {
                    <h1>Введите логин:</h1>
                    <form>
                      <input type="text" name="user">
                      <input type="submit" value="Войти">
                    </form>
                }
                $else
                {
                    <h1>Добро пожаловать, $user!</h1>
                }
                    """)
    print footer()

@http('/logout')
@printhtml
def logout():
    print header(u"Выход")
    print u'<body BGCOLOR="#E7E3E7">'
    user = get_user()
    set_user(None)
    print html(u"""$if (user) {
              <h1>До встречи, $user!</h1>
                }
                <h2>Вы вышли</h2>""")
    print footer()

start_http_server('localhost:8080')


import webbrowser
webbrowser.open('http://localhost:8080/')
# show_gui()
