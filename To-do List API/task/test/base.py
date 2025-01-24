import sqlite3

from random import choice
from string import ascii_uppercase

import requests
from datetime import date
import datetime
import json

from hstest import CheckResult, DjangoTest

INITIAL_RECORDS = [
    ('task1', 'description1', date.today(), date.today() + datetime.timedelta(days=1), False),


]


class TodoApiToolTest(DjangoTest):
    use_database = True

    str_f_time = "%b. %#d, %Y"

    def check_database(self) -> CheckResult:
        try:
            connection = sqlite3.connect(self.attach.test_database)
            cursor = connection.cursor()

            # select name columns
            cursor.execute("SELECT name FROM PRAGMA_TABLE_INFO('app_todo');")
            result = cursor.fetchall()
            columns = ['task', 'description', 'goal_set_date', 'set_to_complete', 'is_completed']
            columns_from_db = []
            for column in result:
                columns_from_db.append(column[0])
            for column in columns:
                if column not in columns_from_db:
                    return CheckResult.wrong(f"Check the '{column}' field in the model")
            return CheckResult.correct()
        except Exception as error:
            return CheckResult.wrong(str(error))
    # stage2
    def check_multiple_json_response(self) -> CheckResult:
        s = self.check_json_tasks([])
        if s.is_correct != True:
            return s;
        #add to database
        self.insert_into_database(INITIAL_RECORDS)
        s = self.check_json_tasks(INITIAL_RECORDS,
                                  ['id', 'task', 'description', 'goal_set_date', 'set_to_complete', 'is_completed'])
        if s.is_correct != True:
            return s;
        for i in list(range(2)):
            INITIAL_RECORDS.append(
                (''.join(choice(ascii_uppercase) for i in range(12)),
                 ''.join(choice(ascii_uppercase) for i in range(12)), date.today(), date.today() + datetime.timedelta(days=1), True),
            )
        self.insert_into_database([INITIAL_RECORDS[1], INITIAL_RECORDS[2]])
        s = self.check_json_tasks(INITIAL_RECORDS,
                                  ['id', 'task', 'description', 'goal_set_date', 'set_to_complete', 'is_completed'])
        if s.is_correct != True:
            return s;
        return CheckResult.correct()
    def check_one_tesk_request(self):
        s = self.check_json_tasks(INITIAL_RECORDS,
                                  ['id', 'task', 'description', 'goal_set_date', 'set_to_complete', 'is_completed'])
        if s.is_correct != True:
            return s;
        return CheckResult.correct()

    def insert_into_database(self, list_records):
        connection = sqlite3.connect(self.attach.test_database)
        cursor = connection.cursor()
        cursor.executemany(
            "INSERT INTO app_todo "
            " ('task', 'description', 'goal_set_date', 'set_to_complete', 'is_completed')"
            " VALUES (?, ?, ?, ?, ?)",
            list_records
        )
        connection.commit()
        connection.close()
    def check_json_tasks(self, list_records, list_keys=None):
        endpoint = "/api/tasks"
        if list_keys is None:
            list_keys = ['id', 'task', 'description', 'goal_set_date', 'set_to_complete', 'is_completed']
        url = self.get_url() + "api/tasks"
        r = requests.get(url)
        if r.status_code != 200:
            return CheckResult.wrong(
                f"Error when trying to get tasks. The route {endpoint} returns the code {r.status_code}, expected 200")
        json_text = r.content.decode("utf-8")
        jobject = json.loads(json_text)
        if type(jobject) is not list:
            return CheckResult.wrong(f"route {endpoint} should return a task list or an empty list [] in json format")
        if len(list_records)==0:
            if len(jobject) != 0 :
                return CheckResult.wrong(
                    f"If no tasks are added to the database, route {endpoint} should return an empty task list []")
        else:
            if len(jobject) != len(list_records):
                return CheckResult.wrong(
                    f"Route {endpoint} returns the number of tasks different from those added to the database")
            for obj in jobject:
                s = self.check_json_task(obj, list_keys, endpoint)
                if not s.is_correct:
                    return s
            #check each task
            for j in jobject:
                current_url = url+'/'+str(j["id"])+"/"
                route = endpoint+'/'+str(j["id"])
                r = requests.get(current_url)
                if r.status_code != 200:
                    return CheckResult.wrong(
                        f"Error when trying to get one task. The route {route} returns the code {r.status_code}, expected 200")
                json_text = r.content.decode("utf-8")
                obj = json.loads(json_text)
                s = self.check_json_task(obj, list_keys, route)
                if not s.is_correct:
                    return s
        return CheckResult.correct()
    def get_task_from_base(self, id):
        try:
            sql = f"SELECT id, task, description, goal_set_date, set_to_complete, is_completed task FROM app_todo where id={id};"
            connection = sqlite3.connect(self.attach.test_database)
            cursor = connection.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
        except Exception as error:
            return CheckResult.wrong(str(error))
    def check_json_task(self, json_task, list_keys, endpoint):
        for lk in list_keys:
            if lk not in list(json_task.keys()):
                return CheckResult.wrong(f"Route {endpoint}: the json view of the task is missing a key '{lk}'")
        id = json_task['id']
        task_from_db = self.get_task_from_base(id)
        if len(task_from_db) != 1:
            CheckResult.wrong(f"Route {endpoint}: No task with id=1, added earlier, was found in the database")
        task_from_db = list(task_from_db[0])
        for t in task_from_db:
            task_from_db[0] = str(task_from_db)
        task_from_db[len(task_from_db)-1] = str(bool(task_from_db[len(task_from_db)-1]))
        json_data = []
        for lk in list_keys:
            json_data.append(str(json_task[lk]))
        for index, lk in enumerate(json_data):
            if lk not in task_from_db[index]:
                return CheckResult.wrong(f"Route {endpoint}: the value of the key '{list_keys[index]}' in the database is different from what is displayed in the json format.")
        return CheckResult.correct()
