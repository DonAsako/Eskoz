function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}
async function sendContentToPreview(content, id) {
    const response = await fetch(window.CONTENT_PREVIEW_URL, {
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
            // Wire scroll syncing once the preview document exists. Re-measure
            // shortly after, once external CSS (highlight/katex/markdown) has
            // loaded and changed the rendered heights.
            setupScrollSync(document.getElementById(id), iframe);
            setTimeout(() => iframe.__scrollSyncRefresh?.(), 600);
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
            // Heights changed — recompute the heading anchors.
            iframe.__scrollSyncRefresh?.();
        }

    } else {
        console.error("Error :", response.status);
    }
}

/* ------------------------------------------------------------------
 * Scroll sync — keep the markdown textarea and the rendered preview
 * aligned. Headings act as anchors: heading N in the source maps to
 * heading N in the preview, and we interpolate linearly between
 * consecutive anchors so the section you're editing stays in view.
 * With no headings it degrades to a plain proportional sync (the
 * anchor list is just the two [start, end] sentinels).
 * Whichever side you actively scroll "drives"; a short lock stops the
 * follower's programmatic scroll from echoing back.
 * ------------------------------------------------------------------ */

// Source line indices of ATX headings, skipping fenced code blocks.
function headingLines(text) {
    const lines = text.split("\n");
    const out = [];
    let inFence = false;
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        if (/^\s*(```|~~~)/.test(line)) { inFence = !inFence; continue; }
        if (!inFence && /^#{1,6}\s/.test(line)) out.push(i);
    }
    return out;
}

// A hidden mirror replicating the textarea's text layout, used to
// measure the pixel offset of a given source line.
function buildMirror(textarea) {
    const cs = getComputedStyle(textarea);
    const div = document.createElement("div");
    [
        "fontFamily", "fontSize", "fontWeight", "fontStyle", "lineHeight",
        "letterSpacing", "wordSpacing", "textTransform", "textIndent",
        "paddingTop", "paddingRight", "paddingBottom", "paddingLeft",
        "borderTopWidth", "borderRightWidth", "borderBottomWidth", "borderLeftWidth",
        "boxSizing",
    ].forEach((p) => { div.style[p] = cs[p]; });
    div.style.position = "absolute";
    div.style.top = "0";
    div.style.left = "-9999px";
    div.style.visibility = "hidden";
    div.style.whiteSpace = "pre-wrap";
    div.style.wordWrap = "break-word";
    div.style.overflowWrap = "break-word";
    document.body.appendChild(div);
    return div;
}

function editorLineOffset(mirror, textarea, text, lineIndex) {
    mirror.style.width = textarea.clientWidth + "px";
    // Text of every line strictly before `lineIndex`, terminated by the
    // newline that opens `lineIndex` (empty for the first line, so the
    // marker lands at offset 0 rather than one line down).
    const before = lineIndex > 0 ? text.split("\n").slice(0, lineIndex).join("\n") + "\n" : "";
    mirror.textContent = before;
    const marker = document.createElement("span");
    marker.textContent = "​";
    mirror.appendChild(marker);
    const padTop = parseFloat(getComputedStyle(textarea).paddingTop) || 0;
    return Math.max(marker.offsetTop - padTop, 0);
}

// Distance from the preview document top that brings `el` to the top edge.
function previewElOffset(win, el) {
    return el.getBoundingClientRect().top + win.scrollY;
}

function textareaScroller(ta) {
    return {
        kind: "editor",
        el: ta,
        get max() { return ta.scrollHeight - ta.clientHeight; },
        get top() { return ta.scrollTop; },
        set top(v) { ta.scrollTop = v; },
        on(fn) { ta.addEventListener("scroll", fn, { passive: true }); },
    };
}

function iframeScroller(iframe) {
    const win = iframe.contentWindow;
    const doc = () => win.document.scrollingElement || win.document.documentElement;
    return {
        kind: "preview",
        el: iframe,
        win,
        get max() { return doc().scrollHeight - win.innerHeight; },
        get top() { return win.scrollY; },
        set top(v) { win.scrollTo(0, v); },
        on(fn) { win.addEventListener("scroll", fn, { passive: true }); },
    };
}

// Piecewise-linear map of `srcTop` through anchor pairs [{a, b}] (sorted
// ascending on the chosen axis) where `from`/`to` pick the axis fields.
function interpolate(srcTop, anchors, from, to) {
    for (let i = 0; i < anchors.length - 1; i++) {
        const lo = anchors[i];
        const hi = anchors[i + 1];
        if (srcTop <= hi[from]) {
            const span = hi[from] - lo[from];
            const t = span > 0 ? (srcTop - lo[from]) / span : 0;
            return lo[to] + t * (hi[to] - lo[to]);
        }
    }
    return anchors[anchors.length - 1][to];
}

function setupScrollSync(textarea, iframe) {
    if (!textarea || !iframe || iframe.dataset.scrollSync || !iframe.contentWindow) return;
    iframe.dataset.scrollSync = "true";

    const editor = textareaScroller(textarea);
    const preview = iframeScroller(iframe);
    const mirror = buildMirror(textarea);

    let anchors = [{ ed: 0, pv: 0 }];   // rebuilt on every preview refresh
    // Cached scroll ranges — reading scrollHeight per scroll event forces a
    // reflow and is what made wheeling "mega lent". Refreshed only on rebuild.
    let editorMax = 0;
    let previewMax = 0;

    function rebuild() {
        const win = preview.win;
        const doc = win.document;
        const headings = doc ? doc.querySelectorAll("h1, h2, h3, h4, h5, h6") : [];
        const lines = headingLines(textarea.value);
        const n = Math.min(lines.length, headings.length);

        editorMax = Math.max(editor.max, 0);
        previewMax = Math.max(preview.max, 0);

        const pairs = [{ ed: 0, pv: 0 }];
        for (let i = 0; i < n; i++) {
            const ed = editorLineOffset(mirror, textarea, textarea.value, lines[i]);
            const pv = previewElOffset(win, headings[i]);
            const prev = pairs[pairs.length - 1];
            // keep strictly increasing on both axes so interpolation is sane
            if (ed > prev.ed && pv > prev.pv) pairs.push({ ed, pv });
        }
        pairs.push({ ed: editorMax, pv: previewMax });
        // guard the end sentinel against the previous anchor
        const last = pairs[pairs.length - 1];
        const prev = pairs[pairs.length - 2];
        if (prev && (last.ed <= prev.ed || last.pv <= prev.pv)) pairs.pop();
        anchors = pairs;
    }

    // Last value we programmatically wrote to each side. A scroll event whose
    // position matches the expected value is our own echo — ignore it. This
    // kills the "rollback" jitter: a follower target that overshoots its max
    // gets clamped, and the clamped echo still matches (no reverse drive).
    const expected = { editor: -1, preview: -1 };
    const maxOf = (kind) => (kind === "editor" ? editorMax : previewMax);

    // Coalesce follower writes into one per animation frame so a burst of
    // scroll/wheel events doesn't thrash layout.
    let rafId = null;
    const queued = { editor: null, preview: null };
    function flush() {
        rafId = null;
        for (const kind of ["editor", "preview"]) {
            const v = queued[kind];
            if (v == null) continue;
            queued[kind] = null;
            const pane = kind === "editor" ? editor : preview;
            expected[kind] = v;
            if (Math.abs(pane.top - v) > 1) pane.top = v;
        }
    }
    function queueFollow(kind, value) {
        queued[kind] = Math.round(Math.max(0, Math.min(value, maxOf(kind))));
        if (!rafId) rafId = requestAnimationFrame(flush);
    }

    function drive(src, dst, from, to) {
        // Echo from our own programmatic scroll → skip.
        if (Math.abs(src.top - expected[src.kind]) <= 1) {
            expected[src.kind] = -1;
            return;
        }
        queueFollow(dst.kind, interpolate(src.top, anchors, from, to));
    }

    editor.on(() => drive(editor, preview, "ed", "pv"));
    preview.on(() => drive(preview, editor, "pv", "ed"));
    window.addEventListener("resize", debounce(rebuild, 150));

    // The mouse wheel is often routed to the long admin page rather than the
    // pane under the cursor, so the pane never fires `scroll` and nothing
    // syncs. Capture the wheel, apply it to the pane ourselves (no read-after-
    // write — we compare against cached max), then let the native scroll drive
    // the sync. preventDefault only when the pane actually moves; at its limit
    // we let the page scroll normally.
    const WHEEL_SPEED = 2.2;   // multiplier — panes scroll faster than the raw delta
    const wheelPixels = (e) => {
        let px;
        if (e.deltaMode === 1) px = e.deltaY * 16;                          // lines
        else if (e.deltaMode === 2) px = e.deltaY * (preview.win.innerHeight || 600); // pages
        else px = e.deltaY;                                                 // pixels
        return px * WHEEL_SPEED;
    };
    const captureWheel = (pane) => (e) => {
        const before = pane.top;
        const next = Math.max(0, Math.min(before + wheelPixels(e), maxOf(pane.kind)));
        if (next !== before) {
            e.preventDefault();
            pane.top = next;
        }
    };
    textarea.addEventListener("wheel", captureWheel(editor), { passive: false });
    preview.win.addEventListener("wheel", captureWheel(preview), { passive: false });

    rebuild();
    iframe.__scrollSyncRefresh = rebuild;   // called after each preview update
}

function debounce(fn, delay = 250) {
    let timer = null;
    return function (...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
}

/* ==================================================================
 * Editor chrome — toolbar, keyboard shortcuts, smart typing, view
 * modes, fullscreen and a live status bar, layered on the textarea.
 * ================================================================== */

function fireInput(ta) {
    ta.dispatchEvent(new Event("input", { bubbles: true }));
}

// Replace [start,end) with `text`, preserving the native undo stack when
// possible (execCommand), then optionally reselect [selStart,selEnd).
function applyText(ta, start, end, text, selStart, selEnd) {
    ta.focus();
    ta.setSelectionRange(start, end);
    let ok = false;
    try { ok = document.execCommand("insertText", false, text); } catch (e) { ok = false; }
    if (!ok) ta.setRangeText(text, start, end, "end");
    if (selStart != null) ta.setSelectionRange(selStart, selEnd);
    fireInput(ta);
}

// Toggle an inline wrapper (`**`, `*`, `~~`, `` ` ``) around the selection.
function surround(ta, token) {
    const val = ta.value;
    const s = ta.selectionStart;
    const e = ta.selectionEnd;
    const sel = val.slice(s, e);
    const t = token.length;

    if (sel.length >= 2 * t && sel.startsWith(token) && sel.endsWith(token)) {
        const inner = sel.slice(t, sel.length - t);          // already wrapped inside → unwrap
        applyText(ta, s, e, inner, s, s + inner.length);
    } else if (val.slice(s - t, s) === token && val.slice(e, e + t) === token) {
        applyText(ta, s - t, e + t, sel, s - t, s - t + sel.length);  // wrapped just outside → unwrap
    } else {
        applyText(ta, s, e, token + sel + token, s + t, s + t + sel.length);
    }
}

// Toggle a per-line prefix over every line the selection touches.
function toggleLines(ta, makePrefix, stripRe) {
    const val = ta.value;
    const ls = val.lastIndexOf("\n", ta.selectionStart - 1) + 1;
    let le = val.indexOf("\n", ta.selectionEnd);
    if (le < 0) le = val.length;
    const lines = val.slice(ls, le).split("\n");
    const meaningful = lines.filter((l) => l.trim() !== "");
    const allHave = meaningful.length > 0 && meaningful.every((l) => stripRe.test(l));
    const out = lines
        .map((l, i) => (l.trim() === "" ? l : allHave ? l.replace(stripRe, "") : makePrefix(l, i)))
        .join("\n");
    applyText(ta, ls, le, out, ls, ls + out.length);
}

function heading(ta, level) {
    const hashes = "#".repeat(level) + " ";
    toggleLines(
        ta,
        (l) => hashes + l.replace(/^#{1,6}\s+/, ""),
        new RegExp("^#{" + level + "}\\s+"),
    );
}

const toggleQuote = (ta) => toggleLines(ta, (l) => "> " + l, /^\s*>\s?/);
const toggleUl = (ta) => toggleLines(ta, (l) => "- " + l, /^\s*[-*+]\s+/);
const toggleOl = (ta) => toggleLines(ta, (l, i) => `${i + 1}. ` + l, /^\s*\d+\.\s+/);

function link(ta) {
    const s = ta.selectionStart;
    const e = ta.selectionEnd;
    const sel = ta.value.slice(s, e) || "texte";
    const text = `[${sel}](url)`;
    const urlStart = s + 1 + sel.length + 2;
    applyText(ta, s, e, text, urlStart, urlStart + 3);
}

function image(ta) {
    const s = ta.selectionStart;
    const e = ta.selectionEnd;
    const sel = ta.value.slice(s, e) || "alt";
    const text = `![${sel}](url)`;
    const urlStart = s + 2 + sel.length + 2;
    applyText(ta, s, e, text, urlStart, urlStart + 3);
}

// Insert a block on its own lines, padding with blank lines as needed.
function insertBlock(ta, block, caretBack = 0) {
    const val = ta.value;
    const s = ta.selectionStart;
    const before = s > 0 && val[s - 1] !== "\n" ? "\n" : "";
    const after = val[s] && val[s] !== "\n" ? "\n" : "";
    const text = before + block + after;
    const caret = s + before.length + block.length - caretBack;
    applyText(ta, s, ta.selectionEnd, text, caret, caret);
}

const codeBlock = (ta) => insertBlock(ta, "```\n\n```", 4);
const hr = (ta) => insertBlock(ta, "---");
const table = (ta) =>
    insertBlock(ta, "| Colonne | Colonne |\n| --- | --- |\n| Valeur | Valeur |");

// pymdownx.blocks admonition: //// type \n content \n ////
// Four slashes (matches existing content and leaves room to nest a /// block).
const ADMONITION_TYPES = [
    "note", "info", "tip", "success", "warning", "caution", "danger", "error",
    "example", "abstract", "summary", "tldr", "quote", "cite", "question",
    "faq", "help", "bug", "security", "flag", "ctf",
];
const admonition = (ta, type) => insertBlock(ta, `//// ${type}\n\n////`, 5);

function buildAdmonitionDropdown(ta) {
    const wrap = document.createElement("div");
    wrap.className = "md-dropdown";

    const trigger = document.createElement("button");
    trigger.type = "button";
    trigger.className = "md-btn";
    trigger.title = "Admonition (bloc //// type)";
    trigger.innerHTML = '<span class="material-symbols-outlined">note_stack</span>';
    trigger.addEventListener("mousedown", (e) => e.preventDefault());

    const menu = document.createElement("div");
    menu.className = "md-menu";

    const close = () => { menu.classList.remove("is-open"); document.removeEventListener("click", onDoc, true); };
    const onDoc = (e) => { if (!wrap.contains(e.target)) close(); };
    const open = () => { menu.classList.add("is-open"); document.addEventListener("click", onDoc, true); };

    ADMONITION_TYPES.forEach((type) => {
        const item = document.createElement("button");
        item.type = "button";
        item.className = "md-menu__item";
        item.dataset.adm = type;
        item.textContent = type;
        item.addEventListener("mousedown", (e) => e.preventDefault());
        item.addEventListener("click", () => { admonition(ta, type); ta.focus(); close(); });
        menu.appendChild(item);
    });

    trigger.addEventListener("click", () => (menu.classList.contains("is-open") ? close() : open()));
    wrap.appendChild(trigger);
    wrap.appendChild(menu);
    return wrap;
}

function handleTab(ta, ev) {
    ev.preventDefault();
    const INDENT = "  ";
    const val = ta.value;
    const s = ta.selectionStart;
    const e = ta.selectionEnd;
    if (s === e && !ev.shiftKey) {
        applyText(ta, s, e, INDENT, s + INDENT.length, s + INDENT.length);
        return;
    }
    const ls = val.lastIndexOf("\n", s - 1) + 1;
    let le = val.indexOf("\n", e);
    if (le < 0) le = val.length;
    const lines = val.slice(ls, le).split("\n");
    const out = lines.map((l) => (ev.shiftKey ? l.replace(/^( {1,2}|\t)/, "") : INDENT + l)).join("\n");
    applyText(ta, ls, le, out, ls, ls + out.length);
}

function handleEnter(ta, ev) {
    if (ta.selectionStart !== ta.selectionEnd) return;
    const val = ta.value;
    const s = ta.selectionStart;
    const ls = val.lastIndexOf("\n", s - 1) + 1;
    const line = val.slice(ls, s);
    const m = line.match(/^(\s*)([-*+]|\d+\.|>)(\s+)/);
    if (!m) return;
    const [full, indent, marker] = m;
    ev.preventDefault();
    if (line.slice(full.length).trim() === "") {
        applyText(ta, ls, s, indent, ls + indent.length, ls + indent.length); // empty item → exit list
        return;
    }
    let next;
    if (marker === ">") next = "\n" + indent + "> ";
    else if (/\d+\./.test(marker)) next = "\n" + indent + (parseInt(marker, 10) + 1) + ". ";
    else next = "\n" + indent + marker + " ";
    applyText(ta, s, s, next, s + next.length, s + next.length);
}

function wireKeys(ta) {
    ta.addEventListener("keydown", (ev) => {
        if ((ev.metaKey || ev.ctrlKey) && !ev.altKey) {
            const k = ev.key.toLowerCase();
            const map = { b: () => surround(ta, "**"), i: () => surround(ta, "*"), e: () => surround(ta, "`"), k: () => link(ta) };
            if (map[k]) { ev.preventDefault(); map[k](); return; }
        }
        if (ev.key === "Tab") { handleTab(ta, ev); return; }
        if (ev.key === "Enter") { handleEnter(ta, ev); return; }
    });
}

function updateStats(ta, el) {
    const text = ta.value;
    const words = (text.trim().match(/\S+/g) || []).length;
    const mins = Math.max(1, Math.round(words / 200));
    el.textContent = `${words} mot${words > 1 ? "s" : ""} · ${text.length} caractères · ~${mins} min de lecture`;
}

function buildToolbar(ta, shell) {
    const bar = document.createElement("div");
    bar.className = "md-toolbar";

    const iconBtn = (icon, title, run, cls = "md-btn") => {
        const b = document.createElement("button");
        b.type = "button";
        b.className = cls;
        b.title = title;
        b.innerHTML = `<span class="material-symbols-outlined">${icon}</span>`;
        b.addEventListener("mousedown", (e) => e.preventDefault()); // keep textarea selection
        if (run) b.addEventListener("click", () => run());
        return b;
    };

    const groups = [
        [
            ["format_h1", "Titre 1", () => heading(ta, 1)],
            ["format_h2", "Titre 2", () => heading(ta, 2)],
            ["format_h3", "Titre 3", () => heading(ta, 3)],
        ],
        [
            ["format_bold", "Gras (Ctrl/Cmd+B)", () => surround(ta, "**")],
            ["format_italic", "Italique (Ctrl/Cmd+I)", () => surround(ta, "*")],
            ["strikethrough_s", "Barré", () => surround(ta, "~~")],
            ["code", "Code en ligne (Ctrl/Cmd+E)", () => surround(ta, "`")],
        ],
        [
            ["link", "Lien (Ctrl/Cmd+K)", () => link(ta)],
            ["image", "Image", () => image(ta)],
            ["format_quote", "Citation", () => toggleQuote(ta)],
            ["format_list_bulleted", "Liste à puces", () => toggleUl(ta)],
            ["format_list_numbered", "Liste numérotée", () => toggleOl(ta)],
        ],
        [
            ["code_blocks", "Bloc de code", () => codeBlock(ta)],
            ["table_chart", "Tableau", () => table(ta)],
            ["horizontal_rule", "Séparateur", () => hr(ta)],
        ],
    ];
    groups.forEach((group, i) => {
        if (i) bar.appendChild(Object.assign(document.createElement("span"), { className: "md-toolbar__sep" }));
        const g = document.createElement("div");
        g.className = "md-toolbar__group";
        group.forEach(([icon, title, run]) => g.appendChild(iconBtn(icon, title, run)));
        bar.appendChild(g);
    });

    // Admonition dropdown (its own group).
    bar.appendChild(Object.assign(document.createElement("span"), { className: "md-toolbar__sep" }));
    const admGroup = document.createElement("div");
    admGroup.className = "md-toolbar__group";
    admGroup.appendChild(buildAdmonitionDropdown(ta));
    bar.appendChild(admGroup);

    bar.appendChild(Object.assign(document.createElement("div"), { className: "md-spacer" }));

    // View segmented control.
    const seg = document.createElement("div");
    seg.className = "md-seg";
    [["edit_note", "editor", "Éditeur seul"], ["vertical_split", "split", "Côte à côte"], ["visibility", "preview", "Aperçu seul"]]
        .forEach(([icon, mode, title]) => {
            const b = iconBtn(icon, title, null, "md-seg__btn");
            if (mode === "split") b.classList.add("is-active");
            b.addEventListener("click", () => {
                shell.dataset.view = mode;
                seg.querySelectorAll(".md-seg__btn").forEach((x) => x.classList.remove("is-active"));
                b.classList.add("is-active");
            });
            seg.appendChild(b);
        });
    bar.appendChild(seg);

    // Fullscreen toggle.
    const fs = iconBtn("fullscreen", "Plein écran (Échap pour sortir)", null);
    fs.classList.add("md-btn--fs");
    fs.addEventListener("click", () => {
        const on = shell.classList.toggle("is-fullscreen");
        document.body.classList.toggle("md-fullscreen-lock", on);
        fs.querySelector("span").textContent = on ? "fullscreen_exit" : "fullscreen";
    });
    bar.appendChild(fs);

    return bar;
}

/* ------------------------------------------------------------------
 * Image upload — paste or drop an image into the editor; it uploads to
 * the admin endpoint and the `![](url)` markdown is inserted in place,
 * with a placeholder shown while the request is in flight.
 * ------------------------------------------------------------------ */
let uploadSeq = 0;

// On a change page the admin URL ends with `…/<app_label>/<model_name>/<object_id>/change/`.
// Parsing it lets the upload endpoint attach the image to the edited object so it
// appears in the "Markdown Images" inline. The add page has no id → null → bare file.
function currentAdminObject() {
    const m = window.location.pathname.match(/\/([^/]+)\/([^/]+)\/([^/]+)\/change\/?$/);
    if (!m) return null;
    return { app_label: m[1], model_name: m[2], object_id: decodeURIComponent(m[3]) };
}

function uploadImage(file) {
    const body = new FormData();
    body.append("image", file);
    const obj = currentAdminObject();
    if (obj) {
        body.append("app_label", obj.app_label);
        body.append("model_name", obj.model_name);
        body.append("object_id", obj.object_id);
    }
    return fetch(window.IMAGE_UPLOAD_URL, {
        method: "POST",
        headers: { "X-CSRFToken": getCookie("csrftoken") },
        body,
    }).then((r) => (r.ok ? r.json() : r.json().then((e) => Promise.reject(e))));
}

function replaceFirst(ta, needle, replacement) {
    const idx = ta.value.indexOf(needle);
    if (idx < 0) return;
    ta.value = ta.value.slice(0, idx) + replacement + ta.value.slice(idx + needle.length);
    fireInput(ta);
}

function insertImageUpload(ta, file) {
    const placeholder = `![⏳ envoi ${++uploadSeq}…]()`;
    const s = ta.selectionStart;
    applyText(ta, s, ta.selectionEnd, placeholder, s + placeholder.length, s + placeholder.length);

    const alt = (file.name || "image").replace(/\.[^.]+$/, "");
    uploadImage(file)
        .then(({ url }) => replaceFirst(ta, placeholder, `![${alt}](${url})`))
        .catch((e) => {
            replaceFirst(ta, placeholder, "");
            alert((e && e.error) || "Échec de l'envoi de l'image.");
        });
}

function wireImageUpload(ta) {
    ta.addEventListener("paste", (e) => {
        const items = e.clipboardData && e.clipboardData.items;
        if (!items) return;
        for (const it of items) {
            if (it.kind === "file" && it.type.startsWith("image/")) {
                const file = it.getAsFile();
                if (file) { e.preventDefault(); insertImageUpload(ta, file); }
            }
        }
    });

    const hasImage = (e) => e.dataTransfer && Array.from(e.dataTransfer.items || []).some((i) => i.type.startsWith("image/"));
    ta.addEventListener("dragover", (e) => { if (hasImage(e)) { e.preventDefault(); ta.classList.add("md-dragover"); } });
    ta.addEventListener("dragleave", () => ta.classList.remove("md-dragover"));
    ta.addEventListener("drop", (e) => {
        const files = e.dataTransfer && e.dataTransfer.files;
        ta.classList.remove("md-dragover");
        if (!files || !files.length) return;
        let handled = false;
        for (const file of files) {
            if (file.type.startsWith("image/")) { insertImageUpload(ta, file); handled = true; }
        }
        if (handled) e.preventDefault();
    });
}

function enhanceEditor(textarea) {
    const content = textarea.closest(".editor-content");
    if (!content || content.dataset.enhanced) return;
    content.dataset.enhanced = "true";

    const shell = document.createElement("div");
    shell.className = "md-editor";
    shell.dataset.view = "split";
    content.parentNode.insertBefore(shell, content);

    const status = document.createElement("div");
    status.className = "md-status";

    shell.appendChild(buildToolbar(textarea, shell));
    shell.appendChild(content);
    shell.appendChild(status);

    wireKeys(textarea);
    wireImageUpload(textarea);
    const refreshStats = () => updateStats(textarea, status);
    textarea.addEventListener("input", refreshStats);
    refreshStats();
}

// Escape leaves fullscreen from anywhere.
document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    const full = document.querySelector(".md-editor.is-fullscreen");
    if (!full) return;
    full.classList.remove("is-fullscreen");
    document.body.classList.remove("md-fullscreen-lock");
    const fsIcon = full.querySelector(".md-btn--fs .material-symbols-outlined");
    if (fsIcon) fsIcon.textContent = "fullscreen";
});

function initTextareas(textareas) {
    textareas.forEach((textarea) => {
        if (textarea.dataset.listenerAttached || textarea.id.includes('__prefix__')) return;

        textarea.dataset.listenerAttached = "true";
        const id = textarea.id;

        enhanceEditor(textarea);
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
