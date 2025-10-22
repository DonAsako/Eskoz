document.addEventListener("DOMContentLoaded", function () {
    const otpIsActiveInput = document.querySelector("#id_profile-0-otp_is_active");
    const qrCodeWrapper = document.querySelector("div.field-qr_code");
    const otpCodeWrapper = document.querySelector("div.field-otp_code");
    const IsActive = otpIsActiveInput.checked
    if (!otpIsActiveInput) return;

    function toggleOtpFields() {
        if (otpIsActiveInput.checked) {
            qrCodeWrapper.style.display = "block";
            otpCodeWrapper.style.display = "block";
        } else {
            qrCodeWrapper.style.display = "none";
            otpCodeWrapper.style.display = "none";
        }

        if (IsActive){
            otpCodeWrapper.style.display = 'none';
        }
    }

    otpIsActiveInput.addEventListener("change", toggleOtpFields);
    toggleOtpFields();
});
