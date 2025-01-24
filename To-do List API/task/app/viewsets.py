from app.models import Todo
from app.serializers import TodoSerializer
from rest_framework import viewsets


class TodoViewset(viewsets.ModelViewSet):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
