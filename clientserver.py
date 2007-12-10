# -*- coding: cp1251 -*-

from pony.thirdparty import sqlite
from pony.main import *

use_autoreload()

@printhtml
def header(title=u'Книги-почтой'):
    print u'<title>%s</title>' % title
    print u'<h1>%s</h1>' % title

@printhtml
def footer():
    print u'<p>Возврат <a href="/">на гл. страницу</a>'
    
@http('/')
@printhtml
def index():
    print header()
    print u'<body BGCOLOR="#E7E3E7">'
    print u"<h1>Добро пожаловать в наш магазин!</h1>"
    print u"Выберите интересующее вас действие:"
    print "<ul>"
    print "<li>%s</li>" % link(u"Регистрация", register)
    print "</ul>"
    user = get_user()
    session = get_session()
    print html(u"""$if (user)
                        {
                   <h2>Здравствуйте, $user!</h2>
              <p>session['x'] = $(session['x']) 
              <p>$link(u"Выйти", logout)
            }
            $else
            {
              <h2>Вы не вошли</h2>
              <p>$link(u"Войти", login)
            }""")

@http('/register')
@printhtml
def register():
    print header(u'Регистрация')
    print u'<body BGCOLOR="#E7E3E7">'
    f=Form()
    f.country = Select('Select your country',required=True,options=['','USA','Australia','Russia'])
    f.ok=Submit(value=u'Далее')
    if f.country.value in ('USA','Australia'):
        f.secure = True # Make multi-step form secure only on last step
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
