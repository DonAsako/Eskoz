const Editor = toastui.Editor;


document.addEventListener("DOMContentLoaded", function () {
  const textarea = document.getElementById("textarea-content");

  const editor = new Editor({
    el: document.getElementById("editor-content"),
    height: "auto",
    initialEditType: "markdown",
    initialValue: textarea.value,
    previewStyle: "vertical",
    plugins: [Editor.plugin.codeSyntaxHighlight, latexPlugin],
  });
  textarea.closest("form").addEventListener("submit", function () {
    textarea.value = editor.getMarkdown();
  });
});
