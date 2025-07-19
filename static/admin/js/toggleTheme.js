function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute("data-theme");
    const newTheme = currentTheme === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", newTheme);
    localStorage.setItem("theme", newTheme);
    updateThemeIcon(newTheme);
    updateIframeTheme(newTheme);
}
function updateThemeIcon(theme) {
    const icon = document.getElementById("themeIcon");
    icon.textContent = theme === "dark" ? "🌙" : "☀️";
}
document.addEventListener("DOMContentLoaded", () => {
    const savedTheme = localStorage.getItem("theme") || "light";
    document.documentElement.setAttribute("data-theme", savedTheme);
    updateThemeIcon(savedTheme);
    updateIframeTheme(savedTheme);
});

function updateIframeTheme(theme) {
  const iframe = document.querySelector("iframe");
  if (!iframe?.contentDocument) return;
  const doc = iframe.contentDocument;
  doc.documentElement.setAttribute("data-theme", theme);
}
