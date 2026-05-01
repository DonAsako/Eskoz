document.addEventListener("DOMContentLoaded", function () {
    const isActiveInput = document.querySelector("#id_two_factor-0-is_active");
    const qrCodeWrapper = document.querySelector(".field-qr_code");
    const otpCodeWrapper = document.querySelector(".field-otp_code");
    const backupCodesWrapper = document.querySelector(".field-backup_codes_display");

    if (!isActiveInput) return;

    const wasAlreadyActive = isActiveInput.checked;

    function toggleOtpFields() {
        const isChecked = isActiveInput.checked;
        const stateChanged = isChecked !== wasAlreadyActive;

        // Show QR code only when enabling (not already active, checking the box)
        if (qrCodeWrapper) {
            qrCodeWrapper.style.display = (isChecked && !wasAlreadyActive) ? "block" : "none";
        }

        // Show OTP input when state changes (enabling or disabling)
        if (otpCodeWrapper) {
            otpCodeWrapper.style.display = stateChanged ? "block" : "none";
        }

        // Hide backup codes section if empty (already viewed or not generated)
        if (backupCodesWrapper) {
            const content = backupCodesWrapper.querySelector(".readonly");
            const hasContent = content && content.textContent.trim() !== "";
            backupCodesWrapper.style.display = hasContent ? "block" : "none";
        }
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
