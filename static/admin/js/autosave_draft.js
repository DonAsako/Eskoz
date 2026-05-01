/* Autosave drafts to localStorage.
 *
 * Every ~10s, snapshots the change-form's text/select fields into
 * localStorage under a per-URL key. On next page load, if a snapshot
 * exists that's newer than the form's last load, surfaces a small
 * banner offering to restore. Cleared on successful submit.
 *
 * Skipped fields: file inputs (binary, untrustworthy from JS), password
 * fields, CSRF token, and Django's bookkeeping inputs (`_save`,
 * `_continue`, etc.). Restores are conservative — they only fill fields
 * that are currently empty so a fresher server-side value wins.
 */
(function () {
    "use strict";

    const INTERVAL_MS = 10000;
    const KEY_PREFIX = "eskoz-draft:";

    function getKey() {
        // Per URL (path + query) so each object's draft is isolated.
        return KEY_PREFIX + window.location.pathname + window.location.search;
    }

    function shouldCapture(input) {
        if (!input.name) return false;
        if (input.type === "file") return false;
        if (input.type === "password") return false;
        if (input.type === "hidden" && input.name === "csrfmiddlewaretoken") return false;
        if (input.name.startsWith("_")) return false; // _save, _continue, _addanother
        if (input.disabled) return false;
        return true;
    }

    function snapshot(form) {
        const data = {};
        const inputs = form.querySelectorAll("input, textarea, select");
        inputs.forEach((el) => {
            if (!shouldCapture(el)) return;
            if (el.type === "checkbox" || el.type === "radio") {
                data[el.name + "::" + (el.value || "on")] = el.checked ? "1" : "0";
            } else if (el.tagName === "SELECT" && el.multiple) {
                data[el.name] = Array.from(el.selectedOptions).map((o) => o.value);
            } else {
                data[el.name] = el.value;
            }
        });
        return { ts: Date.now(), data };
    }

    function isEqualValue(input, stored) {
        if (input.type === "checkbox" || input.type === "radio") {
            const key = input.name + "::" + (input.value || "on");
            return (stored[key] === "1") === input.checked;
        }
        if (input.tagName === "SELECT" && input.multiple) {
            const cur = Array.from(input.selectedOptions).map((o) => o.value);
            const want = stored[input.name] || [];
            if (cur.length !== want.length) return false;
            return cur.every((v, i) => v === want[i]);
        }
        return (stored[input.name] || "") === input.value;
    }

    function snapshotMatches(form, snap) {
        const inputs = form.querySelectorAll("input, textarea, select");
        for (const el of inputs) {
            if (!shouldCapture(el)) continue;
            if (snap.data[el.name] === undefined) {
                // checkbox/radio uses composite keys; skip the simple-name lookup
                if (el.type === "checkbox" || el.type === "radio") {
                    const key = el.name + "::" + (el.value || "on");
                    if (snap.data[key] === undefined) continue;
                } else {
                    continue;
                }
            }
            if (!isEqualValue(el, snap.data)) return false;
        }
        return true;
    }

    function restore(form, snap) {
        const inputs = form.querySelectorAll("input, textarea, select");
        inputs.forEach((el) => {
            if (!shouldCapture(el)) return;
            if (el.type === "checkbox" || el.type === "radio") {
                const key = el.name + "::" + (el.value || "on");
                if (snap.data[key] !== undefined) el.checked = snap.data[key] === "1";
            } else if (el.tagName === "SELECT" && el.multiple) {
                const want = snap.data[el.name];
                if (Array.isArray(want)) {
                    Array.from(el.options).forEach((o) => {
                        o.selected = want.indexOf(o.value) !== -1;
                    });
                }
            } else if (snap.data[el.name] !== undefined) {
                el.value = snap.data[el.name];
                // Trigger input event so the live markdown preview picks it up.
                el.dispatchEvent(new Event("input", { bubbles: true }));
                el.dispatchEvent(new Event("change", { bubbles: true }));
            }
        });
    }

    function formatRelative(ts) {
        const diff = Math.max(0, Date.now() - ts);
        const min = Math.round(diff / 60000);
        if (min < 1) return "just now";
        if (min === 1) return "1 minute ago";
        if (min < 60) return min + " minutes ago";
        const h = Math.round(min / 60);
        if (h === 1) return "1 hour ago";
        if (h < 24) return h + " hours ago";
        const d = Math.round(h / 24);
        return d + " day" + (d > 1 ? "s" : "") + " ago";
    }

    function showBanner(form, snap) {
        const banner = document.createElement("div");
        banner.className = "autosave-banner";
        banner.innerHTML =
            '<div class="autosave-banner__text">' +
            '<strong>Unsaved draft</strong> from ' +
            formatRelative(snap.ts) +
            ". Restore it?</div>" +
            '<div class="autosave-banner__actions">' +
            '<button type="button" class="autosave-banner__btn autosave-banner__btn--primary" data-act="restore">Restore</button>' +
            '<button type="button" class="autosave-banner__btn" data-act="discard">Discard</button>' +
            "</div>";

        form.parentNode.insertBefore(banner, form);

        banner.querySelector('[data-act="restore"]').addEventListener("click", () => {
            restore(form, snap);
            banner.remove();
        });
        banner.querySelector('[data-act="discard"]').addEventListener("click", () => {
            try {
                localStorage.removeItem(getKey());
            } catch (_) {}
            banner.remove();
        });
    }

    function indicator() {
        let el = document.querySelector(".autosave-indicator");
        if (el) return el;
        el = document.createElement("div");
        el.className = "autosave-indicator";
        el.textContent = "";
        document.body.appendChild(el);
        return el;
    }

    function flashSaved() {
        const el = indicator();
        el.textContent = "Draft saved";
        el.classList.add("is-visible");
        clearTimeout(el._t);
        el._t = setTimeout(() => el.classList.remove("is-visible"), 1500);
    }

    function init() {
        // Only fire on change-form pages (Django adds these body classes
        // on object add + change). Skips changelist, dashboard, etc.
        const body = document.body;
        if (!body.classList.contains("change-form")) return;

        const f = document.querySelector("#content-main form");
        if (!f) return;

        // Wipe stored draft on submit so a successful save doesn't leave
        // a stale "unsaved" banner on the next visit.
        f.addEventListener("submit", () => {
            try {
                localStorage.removeItem(getKey());
            } catch (_) {}
        });

        // Offer restore if a stored draft is newer-looking than the page.
        try {
            const raw = localStorage.getItem(getKey());
            if (raw) {
                const snap = JSON.parse(raw);
                if (snap && snap.data && !snapshotMatches(f, snap)) {
                    showBanner(f, snap);
                }
            }
        } catch (_) {}

        // Periodic snapshot.
        setInterval(() => {
            try {
                const snap = snapshot(f);
                localStorage.setItem(getKey(), JSON.stringify(snap));
                flashSaved();
            } catch (_) {
                // Quota exceeded or storage unavailable — fail silently.
            }
        }, INTERVAL_MS);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
