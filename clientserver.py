# -*- coding: cp1251 -*-

from pony.thirdparty import sqlite
from pony.main import *

use_autoreload()

@printhtml
def header(title=u'�����-������'):
    print u'<title>%s</title>' % title
    print u'<h1>%s</h1>' % title

@printhtml
def footer():
    print u'<p>������� <a href="/">�� ��. ��������</a>'
    
@http('/')
@printhtml
def index():
    print header()
    print u'<body BGCOLOR="#E7E3E7">'
    print u"<h1>����� ���������� � ��� �������!</h1>"
    print u"�������� ������������ ��� ��������:"
    print "<ul>"
    print "<li>%s</li>" % link(u"�����������", register)
    print "</ul>"
    user = get_user()
    session = get_session()
    print html(u"""$if (user)
                        {
                   <h2>������������, $user!</h2>
              <p>session['x'] = $(session['x']) 
              <p>$link(u"�����", logout)
            }
            $else
            {
              <h2>�� �� �����</h2>
              <p>$link(u"�����", login)
            }""")

@http('/register')
@printhtml
def register():
    print header(u'�����������')
    print u'<body BGCOLOR="#E7E3E7">'
    f=Form()
    f.country = Select('Select your country',required=True,options=['','USA','Australia','Russia'])
    f.ok=Submit(value=u'�����')
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
        f.country.label = u'�������� ������'
        f.city = Select(u'�������� �����', True,options = ['', u'������',u'�����-���������', u'�����������'])
        f.last_name = Text(u'�������', required=True)
        f.fist_name = Text(u'���', required=True)
        f.patronymic_name = Text(u'��������')
        f.sex = RadioGroup(u'���', options=[ u'�������', u'�������' ])
        f.email = Text(u'�������� �����', True)
        f.password = Password(u'������', True)
        f.password2 = Password(u'������� ������ ��� ���', True)
        f.subscribe = Checkbox(u'� ���� �������� �������', value=True)
        f.news_categories = CheckboxGroup(u'��������� ��������',options=[(1,u'��������� �������'),(2,u'�������� �������'),(3,u'������� ���������')],
                                          value=[ 1, 2 ])

    if (f.country.value and f.password.is_submitted
                        and f.password2.is_submitted
                        and f.password.value != f.password2.value):
        if f.country.value == 'Russia': msg = u'������ �� ���������!'
        else: msg = 'Password did not match!'
        f.password.error_text = f.password2.error_text = msg
    print f.html
    print footer()

@http('/login?user=$user')
@printhtml
def login(user=None):
    print header(u"����")
    print u'<body BGCOLOR="#E7E3E7">'
    if user: set_user(user)
    session = get_session()
    session['x'] = 1
    print html(u"""$if (not user)
                {
                    <h1>������� �����:</h1>
                    <form>
                      <input type="text" name="user">
                      <input type="submit" value="�����">
                    </form>
                }
                $else
                {
                    <h1>����� ����������, $user!</h1>
                }
                    """)
    print footer()

@http('/logout')
@printhtml
def logout():
    print header(u"�����")
    print u'<body BGCOLOR="#E7E3E7">'
    user = get_user()
    set_user(None)
    print html(u"""$if (user) {
              <h1>�� �������, $user!</h1>
                }
                <h2>�� �����</h2>""")
    print footer()

start_http_server('localhost:8080')


import webbrowser
webbrowser.open('http://localhost:8080/')
# show_gui()
