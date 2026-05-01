/* Translation tabs.
 *
 * Detects StackedInline groups whose forms each carry a `*-language`
 * select (i.e. AbstractTranslatableMarkdownItemTranslation inlines)
 * and turns the vertical stack into a tab strip — one tab per
 * existing translation, plus a "+" tab to reveal the empty form for
 * adding a new language.
 *
 * No backend changes; pure DOM rewrite on top of Django's stock
 * inline markup. Stays compatible with formset:added so dynamically
 * added rows get a tab too.
 */
(function () {
    "use strict";

    function getLanguageLabel(select) {
        if (!select) return "";
        const opt = select.options[select.selectedIndex];
        return opt && opt.value ? opt.text : "";
    }

    function getLanguageCode(select) {
        if (!select) return "";
        return select.value || "";
    }

    function findLanguageSelect(form) {
        return form.querySelector('select[name$="-language"]');
    }

    function isTranslationGroup(group) {
        const forms = group.querySelectorAll(".inline-related:not(.empty-form)");
        if (forms.length === 0) {
            // Brand-new object: only the empty form exists. Still treat
            // the group as translations if the empty form has a language
            // select.
            const empty = group.querySelector(".inline-related.empty-form");
            return !!(empty && findLanguageSelect(empty));
        }
        return Array.from(forms).every((f) => findLanguageSelect(f));
    }

    function buildTabBar(group) {
        const bar = document.createElement("div");
        bar.className = "translation-tabs";
        bar.setAttribute("role", "tablist");
        return bar;
    }

    function renderTab(label, code, active) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "translation-tabs__tab" + (active ? " is-active" : "");
        btn.dataset.lang = code;
        btn.setAttribute("role", "tab");
        btn.setAttribute("aria-selected", active ? "true" : "false");
        btn.textContent = label || code || "—";
        return btn;
    }

    function renderAddTab() {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "translation-tabs__tab translation-tabs__add";
        btn.dataset.action = "add";
        btn.setAttribute("aria-label", "Add translation");
        btn.textContent = "+";
        return btn;
    }

    function activate(group, lang) {
        const forms = group.querySelectorAll(".inline-related");
        forms.forEach((form) => {
            if (form.classList.contains("empty-form")) return;
            const select = findLanguageSelect(form);
            const code = getLanguageCode(select);
            const isActive = code === lang;
            form.classList.toggle("is-hidden-tab", !isActive);
        });
        const bar = group.querySelector(".translation-tabs");
        if (bar) {
            bar.querySelectorAll(".translation-tabs__tab").forEach((t) => {
                const isActive = t.dataset.lang === lang;
                t.classList.toggle("is-active", isActive);
                t.setAttribute("aria-selected", isActive ? "true" : "false");
            });
        }
    }

    function showAddForm(group) {
        // Trigger Django's "Add another" link so the standard formset
        // machinery clones the empty form. Then activate the brand-new
        // row's tab.
        const addLink = group.querySelector(".add-row a");
        if (addLink) addLink.click();
    }

    function refreshTabs(group) {
        const bar = group.querySelector(".translation-tabs");
        if (!bar) return;
        // Wipe and rebuild — keeps things simple and idempotent.
        bar.innerHTML = "";

        const forms = Array.from(
            group.querySelectorAll(".inline-related:not(.empty-form)")
        );

        let activeCode = null;
        const previouslyActive = group.dataset.activeLang;

        forms.forEach((form) => {
            const select = findLanguageSelect(form);
            const code = getLanguageCode(select);
            const label = getLanguageLabel(select);
            const isActive =
                (previouslyActive && code === previouslyActive) ||
                (!previouslyActive && activeCode === null);
            if (isActive) activeCode = code;
            const tab = renderTab(label, code, isActive);
            tab.addEventListener("click", () => {
                group.dataset.activeLang = code;
                activate(group, code);
            });
            // Re-render label live when the user changes the language
            // select inside the form.
            if (select && !select.dataset.tabBound) {
                select.dataset.tabBound = "true";
                select.addEventListener("change", () => refreshTabs(group));
            }
            bar.appendChild(tab);
        });

        const addTab = renderAddTab();
        addTab.addEventListener("click", () => showAddForm(group));
        bar.appendChild(addTab);

        if (activeCode !== null) {
            activate(group, activeCode);
        }
    }

    function enhance(group) {
        if (group.dataset.translationTabs) return;
        if (!isTranslationGroup(group)) return;
        group.dataset.translationTabs = "true";
        group.classList.add("inline-group--translation-tabs");

        const header = group.querySelector("h2, .tabular caption, .stacked > h2");
        const bar = buildTabBar(group);
        if (header && header.parentNode) {
            header.parentNode.insertBefore(bar, header.nextSibling);
        } else {
            group.insertBefore(bar, group.firstChild);
        }
        refreshTabs(group);
    }

    function init() {
        document.querySelectorAll(".inline-group").forEach(enhance);
    }

    document.addEventListener("DOMContentLoaded", init);

    document.addEventListener("formset:added", (e) => {
        const newForm = e.target;
        const group = newForm.closest(".inline-group");
        if (!group) return;
        if (!group.dataset.translationTabs) {
            enhance(group);
            return;
        }
        // Newly added row should become the active tab so the user
        // lands on the form they just opened.
        const select = findLanguageSelect(newForm);
        if (select) {
            const code = getLanguageCode(select);
            if (code) group.dataset.activeLang = code;
            select.addEventListener("change", () => {
                group.dataset.activeLang = select.value;
                refreshTabs(group);
            });
        }
        refreshTabs(group);
    });
})();
