# Theme reference

Complete reference for template blocks, context variables, and components
available to theme authors.

## Template blocks

All blocks are defined in `base.html`. Child templates override only what they
need; everything else uses the default from `base.html`.

### Head — SEO & meta

| Block | Default value | Override when |
|---|---|---|
| `title` | *(empty)* | Every page — appended after the site name |
| `meta_description` | `site_settings.seo_settings.meta_description` | Detail pages with specific descriptions |
| `meta_keywords` | `site_settings.seo_settings.meta_keywords` | Rarely needed |
| `meta_author` | `site_settings.seo_settings.meta_author` | Author pages |
| `canonical` | `CANONICAL_URL` | Almost never — auto-computed |
| `robots` | *(empty)* | Password-protected pages (`noindex, nofollow`) |
| `head` | *(empty)* | Any extra `<link>` / `<script>` for a specific page |

### Open Graph

| Block | Default value |
|---|---|
| `og_type` | `website` |
| `og_title` | `site_settings.site_name` |
| `og_description` | `site_settings.seo_settings.og_description` |
| `og_url` | `CANONICAL_URL` |
| `og_site_name` | `site_settings.site_name` |
| `og_locale` | `OG_LOCALE` + alternate locale tags |
| `og_image` | `site_settings.seo_settings.og_image` |
| `meta_properties` | *(empty)* — extra `<meta property="…">` |

Article and writeup templates typically override `og_type` (`article`),
`og_title`, `og_description`, and `og_image` with the object's own fields.

### Twitter card

| Block | Default value |
|---|---|
| `twitter` | Full Twitter card block (card type, creator, title, description, image) |

Override the entire `twitter` block, or override the individual `og_*` blocks
— the defaults mirror the OG values.

### Structured data

| Block | Default |
|---|---|
| `structured_data` | *(empty)* |

Add JSON-LD here for articles, breadcrumbs, etc.:

```django
{% block structured_data %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{{ article.title }}"
}
</script>
{% endblock %}
```

### Body

| Block | Notes |
|---|---|
| `content` | Main page content — everything inside `<main>` |
| `scripts` | Inline or `<script src>` tags at the end of `<body>` |

---

## Context variables

Every template automatically receives the following variables from context
processors. No view action needed.

### `site_settings`

Site branding and module activation flags, managed via the admin.

```
site_settings
├── site_name              str   — brand name shown in navbar, og:title, tab title
├── logo                   url   — optional logo image URL
├── favicon                url   — favicon URL
├── favicon_mime_type      str
├── footer_credits         html  — safe HTML for footer (supports markdown)
├── under_maintenance      bool  — when True, navbar/footer are hidden; maintenance overlay shown
├── blog
│   ├── is_active               bool
│   ├── activate_articles_page  bool
│   ├── activate_projects_page  bool
│   └── activate_members_page   bool
├── infosec
│   ├── is_active               bool
│   ├── activate_writeups_page  bool
│   ├── activate_cves_page      bool
│   └── activate_certifications_page bool
└── education
    ├── is_active               bool
    └── activate_courses_page   bool
```

Use these flags to conditionally render navbar links — never hardcode them:

```django
{% if site_settings.blog.is_active and site_settings.blog.activate_articles_page %}
  <a href="{% url 'blog:article_list' %}">Blog</a>
{% endif %}
```

### `ACTIVE_THEME`

```
{{ ACTIVE_THEME }}   str — active theme name, e.g. "Eskoz"
```

Use it to build static file paths dynamically:

```django
{% load static %}
<link rel="stylesheet" href="{% static ACTIVE_THEME|add:'/css/style.css' %}">
```

Or just hardcode your theme name — that's fine too if you only maintain one.

### `MARKDOWN_CDN`

CDN URLs and SRI hashes for the markdown rendering libraries included in
`components/markdown_assets.html`. You don't need to reference these directly
unless you build a custom `markdown_assets.html`.

```
MARKDOWN_CDN
├── katex
│   ├── css              str
│   ├── css_sri          str
│   ├── js               str
│   ├── js_sri           str
│   ├── auto_render      str
│   └── auto_render_sri  str
└── highlight
    ├── css_light        str   — stylesheet URL for light code theme
    ├── css_dark         str   — stylesheet URL for dark code theme
    ├── js               str
    └── js_sri           str
```

### Pagination

```
{{ POSTS_PER_PAGE }}          int  — currently selected items per page (from ?per_page= query param)
{{ POSTS_PER_PAGE_CHOICES }}  list — available choices, e.g. [12, 24, 36]
```

Used by `components/per_page_selector.html`. Both are available globally on
every page — include the component wherever you show a paginated list.

### Languages

```
{{ SITE_LANGUAGES }}    list of (code, name) — only languages with published content
{{ PATH_AFTER_LANG }}   str — current URL path with the language prefix stripped
```

Used by `components/language_switcher.html`.

### SEO

```
{{ OG_LOCALE }}             str  — e.g. "fr_FR"
{{ OG_LOCALE_ALTERNATES }}  list — locale codes for hreflang alternates
{{ CANONICAL_URL }}         str  — current page URL with ui params (?per_page, ?page) stripped
```

`CANONICAL_URL` is computed from the request — always use it in `{% block canonical %}`
rather than `{{ request.build_absolute_uri }}` to avoid including pagination noise.

### Django built-ins

```
{{ request }}  — full HttpRequest (request.user, request.GET, request.resolver_match, …)
{{ user }}     — current User or AnonymousUser
{{ messages }} — Django message framework
```

---

## Components

Include components with `{% include %}`. Variables are passed with `with` or
inherited from the view context.

### Navigation & layout

```django
{% include 'components/navbar.html' %}
{% include 'components/footer.html' %}
{% include 'components/toggle_theme.html' %}
{% include 'components/language_switcher.html' %}
{% include 'components/maintenance.html' %}
```

`base.html` already includes all of these — you only need them if you build a
completely custom `base.html`.

### Pagination

```django
{# Requires page_obj from the view #}
{% include 'components/pagination.html' %}
{% include 'components/per_page_selector.html' %}
```

### Filters

```django
{# Requires: categories (queryset), current_category (slug or None) #}
{% include 'components/category_selector.html' %}
```

### Icons

```django
{# name: calendar | clock | folder | bolt | user #}
{% include 'components/icons.html' with name='calendar' %}
```

Renders an inline `<svg>` — no external request, no icon font.

### Markdown

```django
{# In {% block head %} — loads KaTeX + highlight.js from CDN #}
{% include 'components/markdown_assets.html' %}

{# In {% block scripts %} — initialises rendering on page load #}
{% include 'components/markdown_init.html' %}
```

Include both on any page that renders a `content` field from the database.

### Content cards

Each card renders one object as a preview tile. Pass the object with `with`:

```django
{% for article in articles %}
  {% include 'components/article_card.html' with article=article %}
{% endfor %}
```

| Component | Required variable |
|---|---|
| `article_card.html` | `article` |
| `writeup_card.html` | `writeup` |
| `cve_card.html` | `cve` |
| `course_card.html` | `course` |
| `lesson_card.html` | `lesson` |
| `module_card.html` | `module` |
| `certification_card.html` | `certification` |
| `project_card.html` | `project` |
| `member_card.html` | `member` |

### Table of contents & related

```django
{# Sidebar ToC — pass the content object #}
{% include 'components/toc.html' with article=article %}

{# Related articles section at the bottom of a post #}
{% include 'components/post_footer.html' with article=article %}

{# Breadcrumb inside the education module #}
{% include 'components/education_breadcrumb.html' with lesson=lesson %}
```

---

## Django template tags available

No custom template tag library is required. The following are loaded as needed:

```django
{% load i18n %}       {# trans, blocktrans #}
{% load static %}     {# static #}
{% load l10n %}       {# localize, unlocalize #}
```

All standard Django template filters (`date`, `truncatechars`, `slugify`,
`safe`, `linebreaks`, `escape`, etc.) work without any extra `{% load %}`.
