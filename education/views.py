from .models import Course, Module, Lesson

from django.shortcuts import render, get_object_or_404


def course_list(request):
    courses = Course.objects.all()
    return render(request, "education/course_list.html", {"courses": courses})


def module_list(request, slug_course=""):
    modules = Module.objects.all()
    return render(request, "education/course_list.html", {"modules": modules})


def lesson_list(request, slug_course="", slug_module=""):
    course = get_object_or_404(Course, slug=slug_course)
    module = get_object_or_404(Module, slug=slug_module, course=course)
    lessons = Lesson.objects.filter(module=module)
    return render(
        request,
        "education/lesson_list.html",
        {"course": course, "module": module, "lessons": lessons},
    )


def lesson_detail(request, slug_course="", slug_module="", slug_lesson=""):
    course = get_object_or_404(Course, slug=slug_course)
    module = get_object_or_404(Module, slug=slug_module, course=course)

    lesson = get_object_or_404(Lesson, slug=slug_lesson, module=module)

    return render(
        request,
        "education/lesson_detail.html",
        {"course": course, "module": module, "lesson": lesson},
    )
