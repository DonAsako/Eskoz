const Editor = toastui.Editor;

function latexPlugin() {
  const toHTMLRenderers = {
    latex(node) {
      const generator = new window.latexjs.HtmlGenerator({ hyphenate: false });
      const { body } = window.latexjs
        .parse(node.literal, { generator })
        .htmlDocument();

      return [
        { type: "openTag", tagName: "div", outerNewLine: true },
        { type: "html", content: body.innerHTML },
        { type: "closeTag", tagName: "div", outerNewLine: true },
      ];
    },
  };

  return { toHTMLRenderers };
}

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
