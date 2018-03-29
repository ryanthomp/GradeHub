from flask import Flask, render_template, request
from lxml import html
from bs4 import BeautifulSoup
import asyncio
import requests
import re
app = Flask(__name__)
y = 0
x = 3
cont = ""
g = {}
err = False
grd = True
session_requests = requests.session()
ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
login_url = 'https://hac.fultonschools.org/HomeAccess/Account/LogOn?ReturnUrl=%2fHomeAccess'
url = 'https://hac.fultonschools.org/HomeAccess/Content/Student/Assignments.aspx'
print("VARS")


async def student():
    url2 = 'https://hac.fultonschools.org/HomeAccess/Classes/Classwork'
    rslt = session_requests.get(url2, headers=dict(referer=url2))
    tree = html.fromstring(rslt.content)
    nmae = tree.xpath('/html/body/div[1]/div[1]/div/div/ul/li[1]/span/text()')
    nmae = nmae[0]
    return nmae


async def info(content):
    d = {}
    data = []
    soup = BeautifulSoup(content, "lxml")
    r = soup.find('table', {"id": "plnMain_rptAssigmnetsByCourse_dgCourseAssignments_0"})
    firstHeader = soup.find('tr', {"class": "sg-asp-table-data-row"})
    for tag in [firstHeader] + firstHeader.findNextSiblings():
        for tr in tag:
            if tr.name == "td":
                rt = tr.text
                rt = rt.replace("\n", "")
                rt = rt.replace("\r", "")
                rt = rt.replace("*", "")
                rt = rt.rstrip()
                rt = rt.lstrip()
                data.append(rt)
        print(data)
        d["{0}".format(data[2])] = data
        data = []
    print(d)
    return d


async def average(content):
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


async def subj(content):
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
loop = asyncio.get_event_loop()


@app.errorhandler(405)
def page_not_found():
    return render_template('index.html'), 405


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/')
@app.route('/dashboard', methods=['POST'])
def login():
    global x
    global y
    global cont
    global nme
    text = request.form['usrnm']
    username = text.upper()
    text = request.form['pswrd']
    password = text.upper()
    print("Password: %s, Username: %s" % (password, username))
    payload = {
        "Database": "10",
        "LogOnDetails.UserName": username,
        "LogOnDetails.Password": password
    }
    result = session_requests.post(login_url, data=payload, headers=dict(referer=login_url))
    print(result.status_code)
    result = session_requests.get(url, headers=dict(referer=url))
    cont = result.content
    for y in range(10):
        global nsub
        av = loop.run_until_complete(average(result.content))
        sub = loop.run_until_complete(subj(result.content))
        nme = loop.run_until_complete(student())
        if av or sub is not None:
            nsub = sub.replace(" ", "_")
            print(x, sub, av, nsub)
            g["{0}".format(nsub)] = [sub, av]
            x += 1
            y += 1
        else:
            x += 1
            y += 1
    print(g)
    return render_template("table.html", value=g, name=nme)


@app.route('/dashboard/<cls>')
def classes(cls):
    print(cls)
    global cont
    print("classes")
    classinfo = loop.run_until_complete(info(cont))
    for m in range(10):
        if classinfo is not None:
            print(x, classinfo)
            m += 1
    return render_template("class.html", db=classinfo)


if __name__ == "__main__":
    app.run(debug=True)
