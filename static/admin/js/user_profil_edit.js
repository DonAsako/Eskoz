document.addEventListener("DOMContentLoaded", function () {
    const isActiveInput = document.querySelector("#id_two_factor-0-is_active");
    if (!isActiveInput) return;

    // unfold does NOT emit a `.field-<name>` class on readonly fields
    // (qr_code, backup_codes_display), so we can't target those wrappers by
    // name. Instead we locate each row from a stable anchor inside it — the
    // editable input by id, or the data-tfa-field marker we render in the
    // readonly HTML — then climb to the field row (.field-line) to toggle it.
    const rowOf = (el) => (el ? el.closest(".field-line, .form-row") : null);

    const otpRow = rowOf(document.querySelector("#id_two_factor-0-otp_code"));
    const qrMarker = document.querySelector('[data-tfa-field="qr"]');
    const qrRow = rowOf(qrMarker);
    const backupMarker = document.querySelector('[data-tfa-field="backup"]');
    const backupRow = rowOf(backupMarker);

    const wasAlreadyActive = isActiveInput.checked;
    const show = (row, visible) => { if (row) row.style.display = visible ? "" : "none"; };

    function toggleOtpFields() {
        const isChecked = isActiveInput.checked;
        const stateChanged = isChecked !== wasAlreadyActive;

        // QR code: only while enabling (box checked, was not already active).
        show(qrRow, isChecked && !wasAlreadyActive);

        // OTP input: whenever the state is changing (enabling or disabling).
        show(otpRow, stateChanged);

        // Backup codes: only when the marker wraps real content.
        const hasBackup = backupMarker && backupMarker.textContent.trim() !== "";
        show(backupRow, Boolean(hasBackup));
    }

    isActiveInput.addEventListener("change", toggleOtpFields);
    toggleOtpFields();

    // Wire up "Copy" buttons in the 2FA panel.
    document.querySelectorAll(".tfa-copy__btn").forEach((btn) => {
        const original = btn.dataset.copyLabel || btn.textContent.trim();
        btn.addEventListener("click", async () => {
            try {
                await navigator.clipboard.writeText(btn.dataset.clipboardText || "");
                btn.textContent = "✓";
                btn.classList.add("tfa-copy__btn--ok");
                setTimeout(() => {
                    btn.textContent = original;
                    btn.classList.remove("tfa-copy__btn--ok");
                }, 1500);
            } catch (e) {
                btn.textContent = "!";
                setTimeout(() => { btn.textContent = original; }, 1500);
            }
        });
    });
});
