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