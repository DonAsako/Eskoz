document.addEventListener('DOMContentLoaded', function() {
    function toggleActivateFields(inline) {
        const isActiveCheckbox = inline.querySelector('input[name$="-is_active"]');
        if (!isActiveCheckbox) return;

        const activateFields = Array.from(inline.querySelectorAll('div.form-row'))
            .filter(row => row.className.includes('field-activate_'));

        function updateVisibility() {
            activateFields.forEach(row => {
                row.style.display = isActiveCheckbox.checked ? '' : 'none';
                row.style.paddingLeft = "2em";
            });
        }

        updateVisibility();

        isActiveCheckbox.addEventListener('change', updateVisibility);
    }

    const inlines = document.querySelectorAll('.inline-related');
    inlines.forEach(inline => toggleActivateFields(inline));

    const emptyForm = document.querySelector('.inline-related.empty-form');
    if (emptyForm) {
        const observer = new MutationObserver(() => {
            const newInlines = document.querySelectorAll('.inline-related:not(.empty-form)');
            newInlines.forEach(inline => toggleActivateFields(inline));
        });
        observer.observe(emptyForm.parentNode, { childList: true });
    }
});
