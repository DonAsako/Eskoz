from django.urls import path

from .views import course_list, module_list, lesson_list, lesson_detail

app_name = "education"
urlpatterns = [
    path("", course_list, name="course_list"),
    path("<slug:slug_course>/", module_list, name="module_list"),
    path("<slug:slug_course>/<slug:slug_module>/", lesson_list, name="lesson_list"),
    path(
        "<slug:slug_course>/<slug:slug_module>/<slug:slug_lesson>",
        lesson_detail,
        name="lesson_detail",
    ),
]
