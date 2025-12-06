from django.shortcuts import get_object_or_404, render

from apps.core.decorators import feature_active_required

from .models import Course, Lesson, Module


@feature_active_required(module_name="education", feature_name="courses")
def course_list(request):
    courses = Course.objects.all()
    return render(request, "education/course_list.html", {"courses": courses})


@feature_active_required(module_name="education", feature_name="courses")
def module_list(request, slug_course=""):
    course = get_object_or_404(Course, slug=slug_course)
    modules = Module.objects.filter(course=course).order_by("order")
    return render(request, "education/module_list.html", {"course": course, "modules": modules})


@feature_active_required(module_name="education", feature_name="courses")
def lesson_list(request, slug_course="", slug_module=""):
    course = get_object_or_404(Course, slug=slug_course)
    module = get_object_or_404(Module, slug=slug_module, course=course)
    lessons = Lesson.objects.filter(module=module).order_by("order")
    return render(
        request,
        "education/lesson_list.html",
        {"course": course, "module": module, "lessons": lessons},
    )


@feature_active_required(module_name="education", feature_name="courses")
def lesson_detail(request, slug_course="", slug_module="", slug_lesson=""):
    course = get_object_or_404(Course, slug=slug_course)
    module = get_object_or_404(Module, slug=slug_module, course=course)
    lesson = get_object_or_404(Lesson, slug=slug_lesson, module=module)

    lessons = Lesson.objects.filter(module=module).order_by("order")
    lesson_list = list(lessons)

    try:
        current_index = lesson_list.index(lesson)
        prev_lesson = lesson_list[current_index - 1] if current_index > 0 else None
        next_lesson = (
            lesson_list[current_index + 1] if current_index < len(lesson_list) - 1 else None
        )
    except ValueError:
        prev_lesson = None
        next_lesson = None

    return render(
        request,
        "education/lesson_detail.html",
        {
            "course": course,
            "module": module,
            "lesson": lesson,
            "prev_lesson": prev_lesson,
            "next_lesson": next_lesson,
        },
    )
