import json

import requests, re
from lxml import html
from datetime import date

class ReLogin:
    requestSessions = None
    csrf_token = None
    xpath_login_form = "//form[@id='login-form']"
    xpath_csrfmiddlewaretoken = "//form[@id='login-form']/input[@name='csrfmiddlewaretoken']"
    xpath_csrfdrf = "//script[contains(text(),'window.drf')]"
    headers_json = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0'
    }
    headers_html = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
    }
    headers_form_post = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
        'Accept': 'text/html; q=1.0, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/json',
        'X-CSRFTOKEN': 'aeyGvFmHHmormw5RMwP0Q6uc2GLjjZ7CakzOVvbCZ9DeGPU8vcWLD7NAI6wUh0sm',
        'X-Requested-With': 'XMLHttpRequest'


    }
    headers_post = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }
    headers_put = {
        'Content-Type': 'application/json',
        'X-CSRFTOKEN': 'H3s4G3okjqQKYocqHO4cANqEHz0hSyqotlNSV9usjFLqPYQzOStcRUTuiXqxokYi',
        'Content-Length': "202",
        #'Host': 'localhost:8001',
        'Cookie':''
    }

    def __init__(self, url):
        self.url = url
        self.requestSessions = requests.Session()
        #self.requestSessions.proxies = {
        #  'http': 'http://127.0.0.1:8887',
        #  'https': 'http://127.0.0.1:8887',
        #}
        #self.requestSessions.cert ="test\FiddlerRoot.cer"

    def get_status_code(self, url: str):
        status_code = self.requestSessions.get(headers=self.headers_json, url=url).status_code
        return status_code

    def put_task(self, url, content):
        get1url = self.requestSessions.get(url)
        if len(get1url.history) != 0:
            if get1url.history[0].status_code == 301:
                url = url + "/"
        page = self.get_page_content(url)
        root = html.fromstring(page)
        script = root.xpath(self.xpath_csrfdrf)[0]
        text = script.text
        text = text[text.find("csrfToken:"):]
        text = text[text.find("\"") + 1:]
        token = text[:text.find("\"")]
        self.csrf_token = token
        content = '''{
    "id": 1,
    "task": "task",
    "description": "Recently added task",
    "goal_set_date": "2022-01-11",
    "set_to_complete": "2022-01-20",
    "is_completed": false,
    "todo_of": 1
}'''
        self.headers_put['X-CSRFTOKEN'] = self.csrf_token
        self.headers_put['Content-Length'] = str(len(content))
        #self.headers_put['Host'] = url
        cookies = self.requestSessions.cookies.get_dict()
        for c in cookies.keys():
            self.headers_put['Cookie'] += c + "=" + cookies[c] + "; "
        try:
            p = self.requestSessions.put(url, data=content, headers=self.headers_put)
            return p
        except Exception as ex:
            return None

    def get_page_content(self, url: str):
        page = self.requestSessions.get(headers=self.headers_html, url=url).text
        return page
    def get_json_content(self, url: str):
        page = self.requestSessions.get(headers=self.headers_json, url=url).text
        return page
    def login(self, user, password):
        page = self.get_page_content(self.url)
        root = html.fromstring(page)
        input = root.xpath(self.xpath_csrfmiddlewaretoken)[0]
        self.csrf_token = input.attrib['value']

        myobj = {'csrfmiddlewaretoken': self.csrf_token, 'username': user, 'password': '1111', 'next': '/admin/'}
        response = self.requestSessions.post(headers=self.headers_post, data=myobj, url=self.url)

        page = response.content.decode("utf-8")
        root = html.fromstring(page)
        login_form = root.xpath(self.xpath_login_form)
        if len(login_form)!=0:
            raise  Exception("I can't log into django")

    def post_request(self, url, json_data):
        page = self.get_page_content(url)
        root = html.fromstring(page)
        input = root.xpath("//input[@name='csrfmiddlewaretoken']")[0]
        csrftoken = input.attrib['value']
        self.headers_form_post['X-CSRFTOKEN'] = csrftoken
        s = self.requestSessions.post(headers=self.headers_form_post, data=json_data, url=url)
        if s.status_code!=201:
            raise Exception("Error when adding a task")
    def post_task(self, url):
        page = self.get_page_content(url)
        root = html.fromstring(page)
        input = root.xpath("//input[@name='csrfmiddlewaretoken']")[0]
        csrftoken = input.attrib['value']
        self.headers_form_post['X-CSRFTOKEN'] = csrftoken
        json_data={}
        root = html.fromstring(page)
        task = root.xpath("//div[./label[contains(text(), 'Task')]]//input")[0]
        tas_name = task.attrib['name']
        json_data[tas_name] = "Task1"
        description_name = root.xpath("//div[./label[contains(text(), 'Description')]]//textarea")[0].attrib['name']
        json_data[description_name] = "description"
        goal_set_date = root.xpath("//div[./label[contains(text(), 'Goal set date')]]//input[@type='date']")[0].attrib['name']
        today = date.today().strftime("%Y-%m-%d")
        json_data[goal_set_date] = today
        set_to_complete = root.xpath("//div[./label[contains(text(), 'Set to complete')]]//input[@type='date']")[0].attrib['name']
        json_data[set_to_complete] = today
        is_completed = root.xpath("//div[./label[contains(text(), 'Is completed')]]//input[@type='checkbox']")[0].attrib['name']
        json_data[is_completed] = "False"
        todo_of = root.xpath("//div[./label[contains(text(), ' Todo of')]]//select")[0].attrib['name']
        json_data[todo_of] = 1
        json_to_post = json.dumps(json_data)
        get1url = self.requestSessions.get(url)
        if len(get1url.history)!=0:
            if get1url.history[0].status_code==301:
               url=url+"/"
        s = self.requestSessions.post(headers=self.headers_form_post, data=json_to_post, url=url)
        if s.status_code != 201:
            raise Exception("Error when adding a task")
