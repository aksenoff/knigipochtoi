# -*- coding: cp1251 -*-

from pony.thirdparty import sqlite
from pony.main import *

use_autoreload()


@http('/')
@printhtml
def managerindex():
    print u'<body BGCOLOR="#E7E3E7">'
    print u"<h1>ERROR 403: forbidden</h1>"

@http('/management/')
@printhtml
def managerlogin():
    f=open(u"C:\\1")
    sp=f.readlines()
    print u'<body BGCOLOR="#E7E3E7">'
    fpass = Form()
    fpass.passwd = Text(u"������", required=True)
    if not fpass.is_valid:
        print u"<h2>������� ������ ���������:</h2>"
        print fpass
    else:
        if fpass.passwd.value+'\n' in sp:
            print u'�� - ��������!'
        else:
            print u'�� �������?<br>'
            print link(u'� ���������� � ������ :(',managerlogin)

start_http_server('localhost:8081')

import webbrowser
webbrowser.open('http://localhost:8081/management/')