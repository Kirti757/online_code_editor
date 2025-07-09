from django.urls import path,include
from editorapp import views

urlpatterns = [
    path('',views.run_code),
]
