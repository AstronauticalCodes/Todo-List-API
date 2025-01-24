from django.urls import path
from app.views import HomeView, DetailView, ListView
from rest_framework import routers
from .viewsets import TodoViewset

urlpatterns = [
    path('', HomeView.as_view()),
    path('<int:pk>/', DetailView.as_view()),
    # path('api/tasks/', ListView.as_view()),
]

router = routers.SimpleRouter()
router.register(r'api/tasks', TodoViewset)

urlpatterns += router.urls
