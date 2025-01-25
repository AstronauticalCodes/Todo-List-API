import sqlite3

from datetime import date

import datetime
from .relogin import ReLogin

from lxml import html


from hstest import CheckResult, DjangoTest

INITIAL_RECORDS = [
    ('task1', 'description1', date.today(), date.today(), False),


]


class TodoApiToolTest(DjangoTest):
    use_database = True
    # stage3

    def create_superuser(self, username="user"):
        password = "pbkdf2_sha256$260000$2rXQ0TE42C4byfn2C8NjAv$lVp8ZfdOcuOmhMnDs/d4Slr1/9o7pDeN3gL93X/qKOA="
        connection = sqlite3.connect(self.attach.test_database)
        cursor = connection.cursor()
        cursor.executemany(
            "INSERT INTO auth_user "
            " ('password', 'is_superuser', 'username', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined', 'first_name')"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [(password, True, username, 'lastname', 'email', True, True, datetime.datetime.now(), 'fe')]
        )
        result = cursor.fetchall()
        connection.commit()
        connection.close()

    def check_not_logined_tasks(self) -> CheckResult:
        path = "api/tasks"
        url = self.get_url()+path
        relogin = ReLogin(url)
        status_code = relogin.get_status_code(url)
        if status_code != 403:
            return CheckResult.wrong(f"If the user is not logged in, the route {url} should return the code 403, now {status_code}")
        #not logined page
        page = relogin.get_page_content(url)
        root = html.fromstring(page)
        login_link = root.xpath("//a[contains(text(), 'Log in')]")
        if len(login_link) == 0:
            return CheckResult.wrong(f"You should add a login to the browsable API.")

        return CheckResult.correct()

    def check_logined_tasks(self) -> CheckResult:
        path = "api/tasks"
        route = '/'+path
        url = self.get_url() + path
        login_url = self.get_url()+"admin/login/"
        users=['user1', 'user2']
        test_users =[]
        for i, user in enumerate(users):
            test_users.append(user)
            self.create_superuser(user)
            relogin = ReLogin(login_url)
            relogin.login(user, '1111')
            status_code = relogin.get_status_code(url)
            if status_code!=200:
                return CheckResult.wrong(f"After logging in the route {route} should return the code 200, now it's {status_code}")
            page = relogin.get_page_content(url)
            result_checking = self.analize_tasks_page(page, test_users)
            if not result_checking.is_correct:
                return result_checking
        return CheckResult.correct()

    def check_not_logined_task(self) ->CheckResult:
        path = "api/tasks/1"
        route = "/api/tasks/1"
        url = self.get_url() + path
        relogin = ReLogin("")
        status_code = relogin.get_status_code(url)
        if status_code != 403:
            return CheckResult.wrong(
                f"The route {route} should return code 403 for unregistered users, the received code is {status_code}")
        check_result = self.check_logined_task(False)
        if check_result.is_correct:
           return CheckResult.wrong(f"Task editing should not be available to users who are not logged in, route: '{route}'.")
#if task not exists
        path = "api/tasks/2"
        route = "/api/tasks/2"
        url = self.get_url() + path
        status_code = relogin.get_status_code(url)
        if status_code != 403:
            return CheckResult.wrong(
                f"Non-registered users should not be able to see any tasks, then route {route} should return a 403 code, now it is {status_code}")

        return CheckResult.correct()

    def check_logined_not_esixt_task(self)-> CheckResult:
        login_url = self.get_url() + "admin/login/"
        relogin = ReLogin(login_url)
        relogin.login('user1', '1111')
        path = "api/tasks/2"
        url = self.get_url() + path
        status_code = relogin.get_status_code(url)
        if status_code != 404:
            return CheckResult.wrong(f"Route: {url} must return 404 code for logined users, if task with id 2 not exist, "
                                     f"nuw status code is {status_code}")
        return CheckResult.correct();
    def check_logined_task(self, login=True) -> CheckResult:
        path_tasks = "api/tasks"
        route_tasks = "/api/tasks"
        path = "api/tasks/1"
        route = '/api/tasks/1'
        url = self.get_url() + path
        login_url = self.get_url()+"admin/login/"
        users=['user1', 'user2']
        relogin = ReLogin(login_url)
        if login:
            relogin.login(users[0], '1111')
        try:
            relogin.post_task(self.get_url()+path_tasks)
        except:
            return CheckResult.wrong(f"Route {route_tasks}: error when adding a task, please check your model and view in the web interface, try adding a task")

        status_code = relogin.get_status_code(url)
        if status_code!=200:
            return CheckResult.wrong(f"Logged in users must have access to the api route {route}. expected code 200, received code {status_code}")
        page = relogin.get_page_content(url)
        result_checking = self.analize_task_page(page, users)
        if not result_checking.is_correct:
            return result_checking

        return self.check_logined_not_esixt_task()

    def check_edit_task(self) ->CheckResult:
        login_url = self.get_url() + "admin/login/"
        users = ['user1', 'user2']
        #self.create_superuser(users[0])
        relogin = ReLogin(login_url)

        relogin.login(users[0], '1111')
        p = relogin.put_task(self.get_url()+"api/tasks/1", "")
        if p is None:
            return CheckResult.wrong(f"Error with editing task route \"api/tasks/1\"")
        if p.status_code!=200:
            return CheckResult.wrong(f"The user who created the task should be able to edit it, route \"api/tasks/1\", "
                                     f"expected code 200, received code {p.status_code}")
        relogin = ReLogin(login_url)
        relogin.login(users[1], '1111')
        p = relogin.put_task(self.get_url() + "api/tasks/1", "")
        if p is None:
            return CheckResult.wrong(f"Error with editing task route \"api/tasks/1\"")
        if p.status_code!=403:
            return CheckResult.wrong(f"Only the task author can update a task, route \"api/tasks/1\", "
                                     f"expected code 403, received code {p.status_code}")
        return CheckResult.correct()

    def analize_tasks_page(self, page: str, test_users):
        path = "api/tasks"
        route = '/'+path
        url = self.get_url() + path

        root = html.fromstring(page)
        task = root.xpath("//div[./label[contains(text(), 'Task')]]//input")
        if len(task) == 0:
            return CheckResult.wrong(f"The edit task field should be on the page {route} after logging in")
        description = root.xpath("//div[./label[contains(text(), 'Description')]]//textarea")
        if len(description) == 0:
            return CheckResult.wrong(f"The edit Description field should be on the page {route} after logging in")
        goal_set_date = root.xpath("//div[./label[contains(text(), 'Goal set date')]]//input[@type='date']")
        if len(goal_set_date)==0:
            return CheckResult.wrong(f"The edit 'Goal set date' field should be on the page {route} after logging in. The field type - date.")
        set_to_complete = root.xpath("//div[./label[contains(text(), 'Set to complete')]]//input[@type='date']")
        if len(set_to_complete) == 0:
            return CheckResult.wrong(
                f"The edit 'Set to complete' field should be on the page {route} after logging in. The field type - date.")
        is_completed = root.xpath("//div[./label[contains(text(), 'Is completed')]]//input[@type='checkbox']")
        if len(is_completed) == 0:
            return CheckResult.wrong(
                f"The edit 'Is completed' field should be on the page {route} after logging in. The field type - checkbox.")

        todo_of = root.xpath("//div[./label[contains(text(), ' Todo of')]]//select")
        if len(todo_of) == 0:
            return CheckResult.wrong(
                f"The edit 'Todo of' field should be on the page {route} after logging in. The field type - select. In the model it is a foreign key")
        options_users = root.xpath("//div[./label[contains(text(), ' Todo of')]]//select/option")
        if len(options_users) != len(test_users):
            return CheckResult.wrong(f"The number of users added to the system does not match the number displayed in the 'Todo of', page {route}")
        for option in options_users:
            if option.text not in test_users:
                return CheckResult.wrong(f"No user names were found that have already been added to the system. Field 'Todo of', page: {route}")

        return CheckResult.correct()

    def analize_task_page(self, page: str, test_users):
        path = "api/tasks/1"
        url = self.get_url() + path
        route = "/api/tasks/1"

        root = html.fromstring(page)
        task = root.xpath("//div[./label[contains(text(), 'Task')]]//input")
        if len(task) == 0:
            return CheckResult.wrong(f"The edit task field should be on the page {route} after logging in")
        description = root.xpath("//div[./label[contains(text(), 'Description')]]//textarea")
        if len(description) == 0:
            return CheckResult.wrong(f"The edit Description field should be on the page {route} after logging in")
        goal_set_date = root.xpath("//div[./label[contains(text(), 'Goal set date')]]//input[@type='date']")
        if len(goal_set_date)==0:
            return CheckResult.wrong(f"The edit 'Goal set date' field should be on the page after logging in. The field type - date.")
        set_to_complete = root.xpath("//div[./label[contains(text(), 'Set to complete')]]//input[@type='date']")
        if len(set_to_complete) == 0:
            return CheckResult.wrong(
                f"The edit 'Set to complete' field should be on the page after logging in. The field type - date.")
        is_completed = root.xpath("//div[./label[contains(text(), 'Is completed')]]//input[@type='checkbox']")
        if len(is_completed) == 0:
            return CheckResult.wrong(
                f"The edit 'Is completed' field should be on the page after logging in. The field type - checkbox.")

        todo_of = root.xpath("//div[./label[contains(text(), ' Todo of')]]//select")
        if len(todo_of) == 0:
            return CheckResult.wrong(
                f"The edit 'Todo of' field should be on the page after logging in. The field type - select. In the model it is a foreign key")
        options_users = root.xpath("//div[./label[contains(text(), ' Todo of')]]//select/option")
        if len(options_users)!=len(test_users):
            return CheckResult.wrong(f"The number of users added to the system does not match the number displayed in the 'Todo of', route: {route}")
        for option in options_users:
            if option.text not in test_users:
                return CheckResult.wrong(f"No user names were found that have already been added to the system. Field 'Todo of', route: {route}")
        #check delete ability
        delete_button = root.xpath("//button[contains(text(),'DELETE')]")
        if len(delete_button) == 0:
            return CheckResult(f"The service must allow you to delete tasks. There must be a delete button, route: {route}.")
        return CheckResult.correct()
