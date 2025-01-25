from django.db import models


class Todo(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, verbose_name="Todo of")
    task = models.CharField(max_length=50)
    description = models.TextField(max_length=1024, verbose_name="Description")
    goal_set_date = models.DateField()
    set_to_complete = models.DateField()
    is_completed = models.BooleanField()
