from django.urls import path,include
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('empty_vector_database/', views.empty_vector_database, name='empty_vector_database'),
    path('get_all_data/', views.get_all_data, name='get_all_data'),
]