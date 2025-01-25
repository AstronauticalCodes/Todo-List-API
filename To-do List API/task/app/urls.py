from django.urls import path
from app.views import HomeView, DetailView, ListView
from rest_framework.authtoken.views import obtain_auth_token
from django.contrib.auth import views as auth_views
from rest_framework import routers
from .viewsets import TodoViewset
from django.urls import include

urlpatterns = [
    path('', HomeView.as_view()),
    path('<int:pk>/', DetailView.as_view()),
    # path('login/', auth_views.LoginView.as_view(), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # path('api/login/', obtain_auth_token),
    # path('api/logout/', LogoutView.as_view()),
    # path('api/tasks/', ListView.as_view()),
    # path('api-auth/', include('rest_framework.urls')),
    # path('rest-auth/', include('rest_auth.urls')),
    # path('rest-auth/registration/', include('rest_auth.registration.urls')),
]

router = routers.SimpleRouter()
router.register(r'api/tasks', TodoViewset)

urlpatterns += router.urls
