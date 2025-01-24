from django.shortcuts import render
from django.views import View
from .models import Todo
from rest_framework import generics

from .serializers import TodoSerializer


# Create your views here.


class HomeView(View):
    template_name = 'app/index.html'
    model = Todo

    def get(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        todos = self.model.objects.all()
        return render(request, self.template_name, context={'todos': todos})


class DetailView(View):
    template_name = "app/details.html"
    model = Todo

    def get(self, request, pk, *args, **kwargs):
        """
        :param request:
        :param pk:
        :param args:
        :param kwargs:
        :return:
        """
        todo = self.model.objects.get(pk=pk)
        return render(request, self.template_name, context={'todo': todo})


class ListView(generics.ListAPIView):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
