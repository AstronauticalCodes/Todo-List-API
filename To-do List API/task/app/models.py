from django.db import models


class Todo(models.Model):
    task = models.CharField(max_length=50)
    description = models.CharField(max_length=1024)
    goal_set_date = models.DateField()
    set_to_complete = models.DateField()
    is_completed = models.BooleanField()
