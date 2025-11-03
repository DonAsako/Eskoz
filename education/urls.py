from django.urls import path

from .views import course_list, course_detail

app_name = "education"
urlpatterns = [
    path("", course_list, name="course_list"),
    path("<slug:slug>/", course_list, name="course_list"),
    path("<slug:slug>/<slug:slug>/", course_detail, name="course_detail"),
]
