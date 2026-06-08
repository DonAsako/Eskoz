# Creating a theme

A theme is a self-contained folder inside `themes/` that holds all the HTML
templates and static assets (CSS, JS) for a given look and feel. Django picks the
active theme at startup — no code changes needed to switch.

## 1. Scaffold the theme

=== "From scratch (empty templates)"

    ```sh
    python manage.py create_theme MyTheme
    ```

    Creates the full directory structure with empty placeholder files — every
    template stub already exists, you just fill them in.

=== "From an existing theme (copy + rename)"

    ```sh
    python manage.py create_theme MyTheme Eskoz
    ```

    Copies every template and static file from `Eskoz` into `MyTheme`. The
    static subfolder is automatically renamed from `static/Eskoz/` to
    `static/MyTheme/`. Start from here if you want to tweak an existing design
    rather than build from zero.

After scaffolding, the structure is:

```
themes/MyTheme/
├── templates/
│   ├── base.html
│   ├── 400.html
│   ├── 403.html
│   ├── 403_csrf.html
│   ├── 404.html
│   ├── 429.html
│   ├── 500.html
│   ├── core/
│   │   ├── index.html
│   │   ├── page.html
│   │   ├── search.html
│   │   └── tag_detail.html
│   ├── blog/
│   │   ├── article_detail.html
│   │   ├── article_list.html
│   │   ├── article_password.html
│   │   ├── member_list.html
│   │   └── project_list.html
│   ├── education/
│   │   ├── course_list.html
│   │   ├── lesson_detail.html
│   │   ├── lesson_list.html
│   │   └── module_list.html
│   ├── infosec/
│   │   ├── certification_list.html
│   │   ├── cve_list.html
│   │   ├── writeup_detail.html
│   │   ├── writeup_list.html
│   │   └── writeup_password.html
│   └── components/
│       ├── article_card.html
│       ├── category_selector.html
│       ├── certification_card.html
│       ├── course_card.html
│       ├── cve_card.html
│       ├── education_breadcrumb.html
│       ├── footer.html
│       ├── icons.html
│       ├── language_switcher.html
│       ├── lesson_card.html
│       ├── maintenance.html
│       ├── markdown_assets.html
│       ├── markdown_init.html
│       ├── member_card.html
│       ├── module_card.html
│       ├── navbar.html
│       ├── pagination.html
│       ├── per_page_selector.html
│       ├── post_footer.html
│       ├── project_card.html
│       ├── toc.html
│       ├── toggle_theme.html
│       └── writeup_card.html
└── static/
    └── MyTheme/
        ├── css/
        │   ├── style.css
        │   └── markdown.css
        └── js/
            └── script.js
```

## 2. Activate it locally

Set `THEME=MyTheme` in `.env`:

```ini
THEME=MyTheme
```

Then start the dev server (SQLite — no Docker needed during development):

```sh
export DJANGO_SETTINGS_MODULE=eskoz.settings.development
python manage.py runserver
```

The settings load `THEME` from `.env` automatically. Any template or static
file change is picked up on reload.

!!! tip "Static files in development"
    Development settings serve static files via Django's dev server — no
    `collectstatic` needed. Run it only for production.

## 3. Template anatomy

Every page template extends `base.html` and overrides the blocks it needs:

```django
{% extends 'base.html' %}
{% load i18n %}

{# Tab title — site name is prepended automatically #}
{% block title %} - My Page{% endblock %}

{# Optional: override SEO meta per page #}
{% block meta_description %}
  <meta name="description" content="Custom description for this page.">
{% endblock %}
{% block og_type %}<meta property="og:type" content="article">{% endblock %}
{% block og_title %}<meta property="og:title" content="{{ object.title }}">{% endblock %}

{# Include markdown dependencies if the page renders markdown content #}
{% block head %}
  {% include 'components/markdown_assets.html' %}
{% endblock %}

{# Main page markup #}
{% block content %}
  <h1>Hello</h1>
{% endblock %}

{# Scripts at bottom of <body> #}
{% block scripts %}
  {% include 'components/markdown_init.html' %}
{% endblock %}
```

See the [Template reference](theme-reference.md) for the full list of blocks and
available context variables.

## 4. Template pages — what each file does

### `base.html`

The root template. All other templates extend it. It renders the `<head>` with
SEO/OG meta tags, the navbar, the footer, the skip-to-content link, and the
dark/light mode toggle. Override its blocks to change page-level metadata; never
duplicate the nav/footer in child templates.

### Error pages

| File | When rendered |
|---|---|
| `400.html` | Bad request |
| `403.html` | Permission denied |
| `403_csrf.html` | CSRF failure |
| `404.html` | Page not found |
| `429.html` | Rate limit exceeded |
| `500.html` | Server error |

These receive no view-specific context — only the base context processors. Keep
them lightweight (no dynamic data that could fail if the DB is down).

### `core/` pages

| File | URL | Context |
|---|---|---|
| `index.html` | `/` (homepage) | `recent_articles`, `recent_writeups`, `recent_courses` (controlled by site settings) |
| `page.html` | `/pages/<slug>/` | `page` (Page object with `title`, `content` markdown) |
| `search.html` | `/search/` | `query`, `results` (list of mixed content objects), `page_obj` |
| `tag_detail.html` | `/tags/<slug>/` | `tag`, `articles`, `writeups`, `page_obj` |

### `blog/` pages

| File | URL | Context |
|---|---|---|
| `article_list.html` | `/blog/` | `articles` (Page object), `categories`, `current_category`, `page_obj` |
| `article_detail.html` | `/blog/<slug>/` | `article` (title, content, author, tags, published_on, cover) |
| `article_password.html` | `/blog/<slug>/` (protected) | `form` |
| `member_list.html` | `/blog/members/` | `members` (paginated) |
| `project_list.html` | `/blog/projects/` | `projects` (paginated), `categories` |

### `education/` pages

| File | URL | Context |
|---|---|---|
| `course_list.html` | `/education/courses/` | `courses` (paginated), `categories` |
| `module_list.html` | `/education/courses/<slug>/modules/` | `course`, `modules` |
| `lesson_list.html` | `/education/courses/<slug>/modules/<slug>/lessons/` | `module`, `lessons` |
| `lesson_detail.html` | `/education/…/lessons/<slug>/` | `lesson` (title, content), `prev_lesson`, `next_lesson` |

### `infosec/` pages

| File | URL | Context |
|---|---|---|
| `writeup_list.html` | `/infosec/writeups/` | `writeups` (paginated), `categories` |
| `writeup_detail.html` | `/infosec/writeups/<slug>/` | `writeup` (title, content, cve, difficulty, tags) |
| `writeup_password.html` | `/infosec/writeups/<slug>/` (protected) | `form` |
| `cve_list.html` | `/infosec/cves/` | `cves` (paginated), `categories` |
| `certification_list.html` | `/infosec/certifications/` | `certifications` (paginated) |

### `components/`

Reusable partials included with `{% include %}`. They read context variables
passed via the `with` keyword or inherited from the view.

| Component | Purpose | Key variables |
|---|---|---|
| `navbar.html` | Top navigation | `site_settings`, `request` |
| `footer.html` | Bottom section | `site_settings` |
| `toggle_theme.html` | Dark/light switch button | — |
| `language_switcher.html` | Language selector | `SITE_LANGUAGES`, `PATH_AFTER_LANG` |
| `pagination.html` | Prev/Next links | `page_obj` |
| `per_page_selector.html` | Items-per-page dropdown | `POSTS_PER_PAGE`, `POSTS_PER_PAGE_CHOICES` |
| `category_selector.html` | Category filter dropdown | `categories`, `current_category` |
| `icons.html` | Inline SVG icons | `name` (calendar, clock, folder, bolt, user) |
| `markdown_assets.html` | KaTeX + highlight.js CDN | `MARKDOWN_CDN` |
| `markdown_init.html` | Init script for markdown | — |
| `toc.html` | Table of contents sidebar | `article` or `lesson` |
| `post_footer.html` | Related content after article | `article` |
| `education_breadcrumb.html` | Breadcrumb for lessons | `lesson`, `module`, `course` |
| `maintenance.html` | Maintenance overlay | `site_settings.under_maintenance` |
| `article_card.html` | Article preview card | `article` |
| `writeup_card.html` | Writeup preview card | `writeup` |
| `cve_card.html` | CVE preview card | `cve` |
| `course_card.html` | Course preview card | `course` |
| `lesson_card.html` | Lesson preview card | `lesson` |
| `module_card.html` | Module preview card | `module` |
| `certification_card.html` | Certification card | `certification` |
| `project_card.html` | Project card | `project` |
| `member_card.html` | Team member card | `member` |

## 5. Static files

Static files **must** live under `static/<ThemeName>/`, not `static/` directly.
This is how Django's static file finder keeps themes isolated.

```
static/
└── MyTheme/
    ├── css/
    │   ├── style.css      ← main stylesheet
    │   └── markdown.css   ← styles for rendered markdown content
    └── js/
        └── script.js      ← theme JS (dark mode, navbar, etc.)
```

Reference them in templates with the `{% static %}` tag:

```django
{% load static %}
<link rel="stylesheet" href="{% static 'MyTheme/css/style.css' %}">
<script src="{% static 'MyTheme/js/script.js' %}" defer></script>
```

!!! warning "Theme name in static path"
    The subfolder name inside `static/` **must match** the theme name exactly
    (case-sensitive). If your theme is called `MyTheme`, use
    `{% static 'MyTheme/css/style.css' %}`, not `static/css/style.css`.

## 6. Dark / light mode

The base template stores the user's colour preference in `localStorage` under the
key `theme`. Your `script.js` should read and apply it, and toggle on user
interaction. The value is `"dark"` or `"light"`.

Minimal implementation:

```js
const root = document.documentElement;
const stored = localStorage.getItem("theme") || "light";
root.setAttribute("data-theme", stored);

document.getElementById("theme-toggle")?.addEventListener("click", () => {
  const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
  root.setAttribute("data-theme", next);
  localStorage.setItem("theme", next);
});
```

Then in your CSS, scope variables to `[data-theme]`:

```css
:root, [data-theme="light"] {
  --bg: #ffffff;
  --text: #111111;
}
[data-theme="dark"] {
  --bg: #111111;
  --text: #f0f0f0;
}
```

## 7. Internationalisation

All user-facing strings must be translatable. Load `i18n` at the top of every
template and wrap strings with `{% trans %}` or `{% blocktrans %}`:

```django
{% load i18n %}

<h1>{% trans "Latest articles" %}</h1>

{% blocktrans with count=article_count %}
  {{ count }} article published.
{% plural %}
  {{ count }} articles published.
{% endblocktrans %}
```

## 8. Test your theme

Before switching to your theme in production, verify every page works:

```sh
THEME=MyTheme python manage.py runserver
```

Visit each route manually:

- [ ] `/` — homepage
- [ ] `/blog/` — article list
- [ ] `/blog/<slug>/` — article detail
- [ ] `/infosec/writeups/` — writeup list
- [ ] `/infosec/writeups/<slug>/` — writeup detail
- [ ] `/infosec/cves/` — CVE list
- [ ] `/infosec/certifications/` — certifications
- [ ] `/education/courses/` — course list
- [ ] `/education/courses/<slug>/modules/<slug>/lessons/<slug>/` — lesson
- [ ] `/search/?q=test` — search results
- [ ] `/tags/<slug>/` — tag page
- [ ] `/pages/<slug>/` — custom page
- [ ] A non-existent URL → 404 page
- [ ] Maintenance mode (`under_maintenance = True` in admin settings)
- [ ] Language switcher (if multilingual content exists)
