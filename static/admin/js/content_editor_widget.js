function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}
async function sendContentToPreview(content) {
    const response = await fetch("/content_preview/", {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({ content })
    });

    if (response.ok) {
        const data = await response.json();
        iframe = document.querySelector(".editor-content--viewer");
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
                    <link rel="stylesheet" href="/static/css/style.css">
                    
                </head>
                <body class="markdown-body">
                    ${data.html}
                    <script>hljs.highlightAll();</script>
                </body>
            </html>`;
        iframeDoc.open();
        iframeDoc.write(html);
        iframeDoc.close();
        
    } else {
        console.error("Error :", response.status);
    }
}
document.addEventListener("DOMContentLoaded", () => {
    const textarea = document.querySelector(".editor-content--editor");
    sendContentToPreview(textarea.value);
    textarea.addEventListener("input", (e) => {
        console.log(e.target.value)
        sendContentToPreview(e.target.value);
    })
});
