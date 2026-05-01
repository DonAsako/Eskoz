/* Inline visibility toggle.
 *
 * Click a `.status-badge--toggle` in any changelist to open a small
 * popover with the four visibility choices. Pick one, POST to
 * `admin:set_visibility`, and swap the badge's class + label in place.
 *
 * Only renders for Post-like models (visibility_badge_field handles the
 * markup); other status badges remain plain spans.
 */
(function () {
    "use strict";

    const FALLBACK_CHOICES = [
        { value: "public", label: "Public" },
        { value: "unlisted", label: "Unlisted" },
        { value: "protected", label: "Protected" },
        { value: "private", label: "Private" },
    ];

    function getChoices(badge) {
        const raw = badge.dataset.choices;
        if (!raw) return FALLBACK_CHOICES;
        try {
            const parsed = JSON.parse(raw);
            if (Array.isArray(parsed) && parsed.length) return parsed;
        } catch (_) {}
        return FALLBACK_CHOICES;
    }

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(";").shift();
        return "";
    }

    function buildPopover(badge) {
        const pop = document.createElement("div");
        pop.className = "visibility-pop";
        pop.setAttribute("role", "menu");

        const current = badge.dataset.current;
        const choices = getChoices(badge);
        choices.forEach((c) => {
            const item = document.createElement("button");
            item.type = "button";
            item.className =
                "visibility-pop__item" + (c.value === current ? " is-current" : "");
            item.dataset.value = c.value;
            item.setAttribute("role", "menuitem");
            item.innerHTML =
                `<span class="visibility-pop__dot visibility-pop__dot--${c.value}"></span>` +
                `<span class="visibility-pop__label">${c.label}</span>`;
            item.addEventListener("click", (e) => {
                e.stopPropagation();
                apply(badge, c.value, pop);
            });
            pop.appendChild(item);
        });
        return pop;
    }

    function position(pop, badge) {
        const r = badge.getBoundingClientRect();
        pop.style.position = "absolute";
        pop.style.top = window.scrollY + r.bottom + 4 + "px";
        pop.style.left = window.scrollX + r.left + "px";
    }

    let openPop = null;
    let openBadge = null;

    function close() {
        if (openPop && openPop.parentNode) openPop.parentNode.removeChild(openPop);
        openPop = null;
        openBadge = null;
    }

    function open(badge) {
        if (openBadge === badge) {
            close();
            return;
        }
        close();
        const pop = buildPopover(badge);
        document.body.appendChild(pop);
        position(pop, badge);
        openPop = pop;
        openBadge = badge;
    }

    function flash(badge, text, ok) {
        const original = badge.textContent;
        const originalCls = badge.className;
        badge.textContent = text;
        badge.classList.add(ok ? "status-badge--flash-ok" : "status-badge--flash-bad");
        setTimeout(() => {
            badge.textContent = original;
            badge.className = originalCls;
        }, 1400);
    }

    function apply(badge, value, pop) {
        const url = badge.dataset.url;
        if (!url) {
            close();
            return;
        }
        const body = new URLSearchParams({ visibility: value });

        // Optimistic loading state.
        pop.classList.add("is-loading");

        fetch(url, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: body.toString(),
        })
            .then((r) => r.json().then((data) => ({ ok: r.ok, data })))
            .then(({ ok, data }) => {
                if (!ok) {
                    flash(badge, data.message || "Error", false);
                    close();
                    return;
                }
                // Swap class + label.
                badge.className = badge.className
                    .split(" ")
                    .filter(
                        (c) => !c.startsWith("status-badge--") || c === "status-badge--toggle"
                    )
                    .concat(["status-badge--" + data.css])
                    .join(" ");
                badge.dataset.current = data.value;
                badge.textContent = data.label;
                close();
            })
            .catch(() => {
                flash(badge, "Error", false);
                close();
            });
    }

    document.addEventListener("click", (e) => {
        const badge = e.target.closest(".status-badge--toggle");
        if (badge) {
            e.preventDefault();
            open(badge);
            return;
        }
        if (openPop && !openPop.contains(e.target)) close();
    });

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") close();
    });

    window.addEventListener("scroll", close, true);
    window.addEventListener("resize", close);
})();
