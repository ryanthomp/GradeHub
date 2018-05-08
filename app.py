from flask import Flask, render_template, request, session, redirect, url_for
from lxml import html
from werkzeug.contrib.cache import SimpleCache
from bs4 import BeautifulSoup
import requests
import re

app = Flask("Grade Hub")
y = 0
x = 3
d = {}
p = {}
g = {}
c = {}
grd = True
err = False
cache = SimpleCache()
session_requests = requests.session()
app.secret_key = '\x94\x1d\x94\x83@q\xd0\x14\x0f)\xa4\xab\x17\xcdS\xee\x0fb\x17\x85\x8c\xbb\xc6t'
ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
url = 'https://hac.fultonschools.org/HomeAccess/Content/Student/Assignments.aspx'
login_url = 'https://hac.fultonschools.org/HomeAccess/Account/LogOn?ReturnUrl=%2fhomeaccess'
print('RUNNING')


def student():
    print("student")
    if 'name' not in session:
        url2 = 'https://hac.fultonschools.org/HomeAccess/Classes/Classwork'
        reslt = session_requests.get(url2, headers=dict(referer=url2))
        tree = html.fromstring(reslt.content)
        nmae = tree.xpath('/html/body/div[1]/div[1]/div/div/ul/li[1]/span/text()')
        nmae = nmae[0]
        session['name'] = nmae
        print(nmae)
        return nmae
    else:
        nmae = session['name']
        print("IN SESSION STORE")
        print(nmae)
        return nmae


def info(cont, z, cls):
    print("info")
    print("cls_in_info", cls)
    print("n_in_info", z)
    data = []
    de = {}
    soup = BeautifulSoup(cont, "lxml")
    tbl = soup.find("table", {"id": "plnMain_rptAssigmnetsByCourse_dgCourseAssignments_%s" % z})
    for tag in [tbl] + tbl.findChildren('tr'):
        for td in tag:
            if td.name == "td":
                rt = td.text
                rt = rt.replace("\n", "")
                rt = rt.replace("\r", "")
                rt = rt.replace("*", "")
                rt = rt.rstrip()
                rt = rt.lstrip()
                data.append(rt)
        try:
            de["{0}".format(data[2])] = data
            data = []
        except IndexError:
            pass
    de.pop("Assignment", 0)
    print("de_in_info", de)
    print("done main")
    print("except")
    return de


def average(content):
    print("average")
    global y
    global grd
    global err
    err = False
    try:
        tree = html.fromstring(content)
        grade = tree.xpath('//*[@id="plnMain_rptAssigmnetsByCourse_lblOverallAverage_%s"]/text()' % y)
        grade = float(grade[0])
        grade = float("%.2f" % grade)
        if grd is True:
            return grade
    except IndexError:
        err = True
        pass


def subj(content):
    print("subj")
    global err
    while not err:
        try:
            global x
            tree = html.fromstring(content)
            subject = tree.xpath('//*[@id="plnMain_pnlFullPage"]/div[%s]/div[1]/a/text()' % x)
            subject = subject[0]
            subject = subject.strip()
            return subject[18:]
        except IndexError:
            pass


def points(cont, z, cls):
    print("points")
    print(cls)
    print(z)
    v = []
    soup = BeautifulSoup(cont, "lxml")
    tbl = soup.find("table", {"id": 'plnMain_rptAssigmnetsByCourse_dgCourseCategories_%s' % z})
    for tag in [tbl] + tbl.findChildren('tr'):
        for td in tag:
            for font in td:
                for b in font:
                    for txt in b:
                        v.append(txt)
    worth = float(v[-3])
    if worth < 1:
        print(worth)
        worth = worth * 100
        worth = 100 - worth
    else:
        print(worth)
        worth = 100 - worth
    if 10 <= worth or 20 >= worth:
        return worth
    else:
        print(None)
        return None


def task(worth, want, current):
    current = float(ansi_escape.sub('', current))
    print("want", want)
    print("worth", worth)
    print("Current", current)
    final = (100 * float(want) - (100 - float(worth)) * float(current)) / float(worth)
    return "%.2f" % final


def task2(worth, get, current):
    current = float(ansi_escape.sub('', current))
    print("current_in_task2", current)
    final = (float(worth) * float(get) + (100 - float(worth)) * float(current)) / 100
    return "%.2f" % final


@app.route('/login', methods=['POST', 'GET'])
def login():
    print("login")
    print("session_in_login", session)
    if request.method == 'POST':
        global x
        global y
        global c
        text = request.form['usrnm']
        username = text.upper()
        text = request.form['pswrd']
        password = text.upper()
        print("Password: %s, Username: %s" % (password, username))
        if username and password not in session.values():
            print("NOT IN SESSION")
            session['username'] = username
            session['password'] = password
            payload = {
                "Database": "10",
                "LogOnDetails.UserName": username,
                "LogOnDetails.Password": password
            }
            result = session_requests.post(login_url, data=payload, headers=dict(referer=login_url))
            print(result.status_code)
            result = session_requests.get(url, headers=dict(referer=url))
            nme = student()
            session['name'] = nme
            for y in range(10):
                global nsub
                av = average(result.content)
                sub = subj(result.content)
                if av or sub is not None:
                    nsub2 = sub.replace("/", "_")
                    nsub = nsub2.replace(" ", "_")
                    classinfo = info(result.content, y, nsub)
                    point = points(result.content, y, nsub)
                    g["{0}".format(nsub)] = [sub, av, x]
                    c["{0}".format(nsub)] = classinfo
                    p["{0}".format(nsub2)] = point
                    x += 1
                    y += 1
                else:
                    x += 1
                    y += 1
            session['g'] = g
            cache.set('c', c)
            cache.set('p', p)
            return redirect(url_for('dashboard'))
        else:
            session.new = False
            print("IN SESSION")
            return redirect(url_for('dashboard'))


@app.route('/')
def index():
    print("index")
    print("session_in_index", session)
    return render_template("index.html")


@app.route('/dashboard')
def dashboard():
    print("dashboard")
    ge = session['g']
    print("ge_in_dashboard", ge)
    nme = session['name']
    print("nme_in_dashboard", nme)
    return render_template("table.html", value=ge, name=nme)


@app.route('/dashboard/<cls>')
def classes(cls):
    global c
    print("c_in_classes", c)
    print("classes")
    nme = session['name']
    classinfo = c.get(cls)
    print("ce_in_classes", c)
    print("classinfo_in_classes", classinfo)
    return render_template("class.html", name=nme, db=classinfo)


@app.route('/dashboard/tools/final_calc', methods=['POST', 'GET'])
def final_calc():
    print("final calc")
    if request.method == 'POST':
        print("POST")
        cls = request.form.get('class_select')
        print("cls_in_final-calc", cls)
        cls = cls.split(",")
        curr = cls[1]
        cls = cls[0]
        cls = cls.replace("/", "_")
        print("cls_in_final-calc", cls)
        print("curr_in_final-calc", curr)
        want = request.form.get('want')
        print("want_in_final-calc", want)
        worth = cache.get('p')
        print(worth)
        print(cls)
        worth = worth.get(cls)
        print(worth)
        if worth is None:
            return render_template('calc.html', cls=cls, want=want, worth_val=2)
        result = task(worth, want, curr)
        return render_template('result.html', code=1, grade=want, cls=cls, result=result)
    ge = session['g']
    return render_template('calc.html', ge=ge, worth_val=1)


@app.route('/dashboard/tools/final_calc2', methods=['POST', 'GET'])
def final_calc2():
    print("final calc 2")
    if request.method == 'POST':
        print("POST")
        cls = request.form.get('class_select')
        print(cls)
        cls = cls.split(",")
        curr = cls[1]
        cls = cls[0]
        cls = cls.replace("/", "_")
        print(cls)
        print(curr)
        get = request.form.get('get')
        print(get)
        worth = cache.get('p')
        print(worth)
        worth = worth.get(cls)
        print(worth)
        if worth is None:
            return render_template('calc2.html', cls=cls, want=get, worth_val=2)
        result = task2(worth, get, curr)
        return render_template('result.html', code=1, grade=get, cls=cls, result=result)
    ge = session['g']
    return render_template('calc2.html', ge=ge, worth_val=1)


@app.route('/dashboard/tools/gpa_calc')
def gpa_calc():
    print('GPA Calc')
    gpa = 0.0
    classs = 0
    for grades in g.values():
        grade = grades[1]
        classs += 1
        if 100 >= grade >= 97:
            print("A+")
            weight = 4.3
            print(grade)
            gpa += weight

        elif 97 > grade >= 93:
            print("A")
            weight = 4.0
            print(grade)
            gpa += weight

        elif 93 > grade >= 90:
            print("A-")
            weight = 3.7
            print(grade)
            gpa += weight

        elif 90 > grade >= 87:
            print("B+")
            weight = 3.3
            print(grade)
            gpa += weight

        elif 87 > grade >= 83:
            print("B")
            weight = 3.0
            print(grade)
            gpa += weight

        elif 83 > grade >= 80:
            print("B-")
            weight = 2.7
            print(grade)
            gpa += weight

        elif 80 > grade >= 77:
            print("C+")
            weight = 2.3
            print(grade)
            gpa += weight

        elif 77 > grade >= 73:
            print("C")
            weight = 2.0
            print(grade)
            gpa += weight

        elif 73 > grade >= 70:
            print("C-")
            weight = 1.7
            print(grade)
            gpa += weight

        elif 70 > grade >= 67:
            print("D+")
            weight = 1.3
            print(grade)
            gpa += weight

        elif 67 > grade >= 63:
            print("D")
            weight = 1.0
            print(grade)
            gpa += weight

        elif 63 > grade >= 60:
            print("D-")
            weight = 0.7
            print(grade)
            gpa += weight

        elif 60 > grade >= 0:
            print("F")
            weight = 0.0
            print(grade)
            gpa += weight
    finalgpa = float(gpa / classs)
    finalgpa = "%.2f" % finalgpa
    return render_template("result.html", code=2, result=finalgpa)


@app.route('/dashboard/result', methods=['POST', 'GET'])
def rslt():
    print('result')


@app.route('/dashboard/tools')
def tool_dash():
    return render_template("tools.html")


@app.route('/help')
def hlp():
    print("help")
    return render_template("help.html")


@app.route('/logout')
def logout():
    print("logout")
    print(session)
    session.clear()
    print(session)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.config['CACHE_TYPE'] = 'simple'
    app.run()
