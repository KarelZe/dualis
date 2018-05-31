import itertools
from concurrent import futures

import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
from werkzeug.exceptions import abort

app = Flask(__name__)

BASE_URL = "https://dualis.dhbw.de"
units = []


@app.route("/dualis/api/v1.0/semesters/", methods=['GET'])
def get_semesters():
    # TODO: refactor code so that semesters can be accessed through endpoint
    return jsonify({}), 200


@app.route("/dualis/api/v1.0/units/", methods=['GET'])
def get_units():
    # TODO: refactor code so that units and all relating exams can be accessed through endpoint
    return jsonify({}), 200


@app.route("/dualis/api/v1.0/grades/", methods=['GET'])
def get_grades():
    """
    api endpoint to query grades from dualis.dhbw.de. Function expects credentials in GET request
    like {"user":"karel.zeman@dhbw-karlsruhe.de","password":"journeyToTheCenterOftheEarth"}
    :return: grades of all semesters from all modules as json
    """
    if not request.json or not 'password' in request.json or not 'user' in request.json:
        abort(401)
    # TODO: Refactor spaghetti code :)
    # retrieve password and username from body
    request_json = request.get_json()
    user = request_json.get('user')
    password = request_json.get('password')

    # create a session
    url = BASE_URL + "/scripts/mgrqcgi?APPNAME=CampusNet&PRGNAME=EXTERNALPAGES&ARGUMENTS=-N000000000000001,-N000324,-Awelcome"
    cookie_request = requests.get(url)

    data = {"usrname": user, "pass": password,
            "APPNAME": "CampusNet",
            "PRGNAME": "LOGINCHECK",
            "ARGUMENTS": "clino,usrname,pass,menuno,menu_type, browser,platform",
            "clino": "000000000000001",
            "menuno": "000324",
            "menu_type": "classic",
            "browser": "",
            "platform": ""
            }
    # return dualis response code, if response code is not 200
    login_response = requests.post(url, data=data, headers=None, verify=True, cookies=cookie_request.cookies)
    arguments = login_response.headers['REFRESH']
    if not login_response.ok:
        abort(login_response.status_code)

    # redirecting to course results...
    url_content = BASE_URL + "/scripts/mgrqcgi?APPNAME=CampusNet&PRGNAME=STARTPAGE_DISPATCH&ARGUMENTS=" + arguments[79:]
    url_content = url_content.replace("STARTPAGE_DISPATCH", "COURSERESULTS")
    semester_ids_response = requests.get(url_content, cookies=login_response.cookies)
    if not semester_ids_response.ok:
        abort(semester_ids_response.status_code)

    # get ids of all semester, replaces -N ...
    soup = BeautifulSoup(semester_ids_response.content, 'html.parser')
    options = soup.find_all('option')
    semester_ids = [option['value'] for option in options]
    semester_urls = [url_content[:-15] + semester_id for semester_id in semester_ids]

    # search for all unit_urls in parallel
    with futures.ThreadPoolExecutor(8) as semester_pool:
        tmp = semester_pool.map(parse_semester, semester_urls, [login_response.cookies] * len(semester_urls))
    unit_urls = list(itertools.chain.from_iterable(tmp))

    # query all unit_urls to obtain grades in parallel
    with futures.ThreadPoolExecutor(8) as detail_pool:
        semester = detail_pool.map(parse_unit, unit_urls, [login_response.cookies] * len(unit_urls))
    units.extend(semester)

    # find logout url in html source code and logout
    logout_url = BASE_URL + soup.find('a', {'id': 'logoutButton'})['href']
    logout(logout_url, cookie_request.cookies)
    # return dict containing units and exams as valid json

    return jsonify(units), 200


def parse_student_results(url, cookies):
    """
    This function calls the dualis web page of a given semester to query for all modules, that have been finished.
    :param url: url of STUDENT_RESULT page
    :param cookies: cookie of current session
    :return: list of urls for units
    """
    response = requests.get(url=url, cookies=cookies)
    student_result_soup = BeautifulSoup(response.content, "html.parser")
    table = student_result_soup.find("table", {"class": "students_results"})
    return [a['href'] for a in table.find_all("a", href=True)]


def parse_semester(url, cookies):
    """
    function calls the dualis web page of a given a semester to extract the urls of all units within the semester.
    It's searching for script-tags containing the urls and crops away the surrounding javascript.
    :param url: url of the semester page
    :param cookies: cookie for the semester page
    :return: list with urls of all units in semester
    """
    semester_response = requests.get(url, cookies=cookies)
    semester_soup = BeautifulSoup(semester_response.content, 'html.parser')
    table = semester_soup.find("table", {"class": "list"})
    # get unit details from javascript
    return [script.text.strip()[301:414] for script in table.find_all("script")]


def parse_unit(url, cookies):
    """
    function calls the dualis webpage of a given module to extract the grades
    :param url: url for unit page
    :param cookies: cookie for unit page
    :return: unit with information about name and exams incl. grades
    """
    response = requests.get(url=BASE_URL + url, cookies=cookies)
    detail_soup = BeautifulSoup(response.content, "html.parser")
    h1 = detail_soup.find("h1").text.strip()
    table = detail_soup.find("table", {"class": "tb"})
    td = [td.text.strip() for td in table.find_all("td")]
    unit = {'name': h1.replace("\n", " ").replace("\r", ""), 'exams': []}
    # units have non uniform structure. Try to map based on total size.
    if len(td) <= 24:
        exam = {'name': td[13], 'date': td[14], 'grade': td[15], 'externally accepted': False}
        unit['exams'].append(exam)
    elif len(td) <= 29:
        exam = {'name': td[19], 'date': td[14], 'grade': td[21], 'externally accepted': False}
        unit['exams'].append(exam)
    elif len(td) == 30:
        for idx in range(13, len(td) - 5, 6):
            exam = {'name': td[idx], 'date': td[idx + 1], 'grade': td[idx + 2], 'externally accepted': False}
            unit['exams'].append(exam)
    elif len(td) <= 31:
        for idx in range(11, len(td) - 7, 7):
            exam = {'name': td[idx], 'date': td[idx + 3], 'grade': td[idx + 4], 'externally accepted': False}
            unit['exams'].append(exam)
    else:
        for idx in range(19, len(td) - 5, 6):
            exam = {'name': td[idx], 'date': td[14], 'grade': td[idx + 2], 'externally accepted': False}
            unit['exams'].append(exam)
    return unit


def logout(url, cookies):
    """
    Function to perform logout in dualis.dhbw.de
    :param url: url to perform logout
    :param cookies: cookie with session information
    :return: boolean whether logging out was successful
    """
    return requests.get(url=url, cookies=cookies).ok


if __name__ == "__main__":
    app.run(debug=True)
