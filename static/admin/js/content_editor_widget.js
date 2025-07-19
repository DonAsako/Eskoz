function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}
async function sendContentToPreview(content, id) {
    const response = await fetch("/content_preview/", {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({ content })
    });
    const currentTheme = document.documentElement.getAttribute("data-theme");
    console.log(currentTheme);
    const Theme = document.querySelector('meta[name="theme-name"]').getAttribute("content");

    if (response.ok) {
        const data = await response.json();
        const iframe = document.getElementById(`render-${id}`);
        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;

        const html = `
            <!DOCTYPE html>
            <html>
                <head>
                    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/github-markdown-css/github-markdown.min.css">
                    <link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/default.min.css">
                    <script src="//cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>
                    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
                    <style>
                        body{
                            padding: 1em;
                        }
                    </style>
                    <link rel="stylesheet" href="${Theme}/static/css/style.css">
                </head>
                <body class="markdown-body">
                    ${data.html}
                    <script>hljs.highlightAll();</script>
                </body>
            </html>`;
        iframeDoc.open();
        iframeDoc.write(html);
        iframeDoc.documentElement.setAttribute("data-theme", currentTheme);
        iframeDoc.close();
        
    } else {
        console.error("Error :", response.status);
    }
}
function debounce(fn, delay = 250) {
    let timer = null;
    return function (...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
}

function initTextareas(textareas) {
    textareas.forEach((textarea) => {
        if (textarea.dataset.listenerAttached || textarea.id.includes('__prefix__')) return;

        textarea.dataset.listenerAttached = "true";
        const id = textarea.id;
        
        sendContentToPreview(textarea.value, id);

        const smoothUpdate = debounce((value) => {
            sendContentToPreview(value, id);
        }, 250);

        textarea.addEventListener("input", (e) => {
            smoothUpdate(e.target.value);
        });
    });
}


document.addEventListener("DOMContentLoaded", () => {
    const textareas = document.querySelectorAll(".editor-content--editor");
    initTextareas(textareas);
});

document.addEventListener("formset:added", (e) => {
    const newForm = e.target;

    const newTextareas = newForm.querySelectorAll(".editor-content--editor");
    initTextareas(newTextareas);
});