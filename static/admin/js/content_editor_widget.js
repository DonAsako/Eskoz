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
    const Theme = document.querySelector('meta[name="theme-name"]').getAttribute("content");

    if (response.ok) {
        const data = await response.json();
        const iframe = document.getElementById(`render-${id}`);
        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
        const katexRenderOptions = {
            delimiters: [
                { left: "\\[", right: "\\]", display: true },
                { left: "$$", right: "$$", display: true },
                { left: "$", right: "$", display: false },
                { left: "\\(", right: "\\)", display: false }
            ],
            throwOnError: false
        };
        // If iframe is empty (first load), write full HTML
        if (!iframeDoc.body.innerHTML) {
            const html = `
            <!DOCTYPE html>
            <html>
                <head>
                
                    <link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/styles/default.min.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/styles/base16/dracula.min.css" integrity="sha512-zKpFlhUX8c+WC6H/XTJavnEpWFt2zH9BU9vu0Hry5Y+SEgG21pRMFcecS7DgDXIegXBQ3uK9puwWPP3h6WSR9g==" crossorigin="anonymous" referrerpolicy="no-referrer" />

                    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/highlight.min.js" integrity="sha512-EBLzUL8XLl+va/zAsmXwS7Z2B1F9HUHkZwyS/VKwh3S7T/U0nF4BaU29EP/ZSf6zgiIxYAnKLu6bJ8dqpmX5uw==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
                    <style>body{ padding: 1em; }</style>
                    <link rel="stylesheet" href="/static/${Theme}/css/style.css">
                    <link rel="stylesheet" href="/static/${Theme}/css/markdown.css">
                    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.25/dist/katex.min.css" integrity="sha384-WcoG4HRXMzYzfCgiyfrySxx90XSl2rxY5mnVY5TwtWE6KLrArNKn0T/mOgNL0Mmi" crossorigin="anonymous">
                    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.25/dist/katex.min.js" integrity="sha384-J+9dG2KMoiR9hqcFao0IBLwxt6zpcyN68IgwzsCSkbreXUjmNVRhPFTssqdSGjwQ" crossorigin="anonymous"></script>
                    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.25/dist/contrib/auto-render.min.js" integrity="sha384-hCXGrW6PitJEwbkoStFjeJxv+fSOOQKOPbJxSfM6G5sWZjAyWhXiTIIAmQqnlLlh" crossorigin="anonymous"
                            onload="renderMathInElement(document.body);"></script>
                </head>
                <body>
                    <div class="article--container">
                        <div class="article--wrapper">
                            <div class="article--content markdown-body">
                                ${data.html}
                            </div>
                        </div>
                    </div>
                    <script>
                        document.addEventListener("DOMContentLoaded", function() {
                            hljs.highlightAll();
                            renderMathInElement(document.body, ${JSON.stringify(katexRenderOptions)});
                        });
                    </script>
                </body>
            </html>`;
            iframeDoc.open();
            iframeDoc.write(html);
            iframeDoc.documentElement.setAttribute("data-theme", currentTheme);
            iframeDoc.close();
        } else {
            const contentContainer = iframeDoc.querySelector(".article--content");
            contentContainer.innerHTML = data.html;
            iframe.contentWindow.hljs.highlightAll();
            
            if (iframe.contentWindow.renderMathInElement) {
                iframe.contentWindow.renderMathInElement(
                    iframeDoc.body,
                    katexRenderOptions
                );
            }
        }

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
