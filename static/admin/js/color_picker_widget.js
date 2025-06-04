document.addEventListener('DOMContentLoaded', () => {
    const colorPickers = document.querySelectorAll(".color-picker--wrapper");

    colorPickers.forEach(picker => {
        const ColorPicker = picker.querySelector(".color-picker--picker");
        const ColorInput = picker.querySelector(".color-picker--input");
        if (!ColorPicker || !ColorInput) return;

        function update_color(value) {
            ColorPicker.value = value;
            ColorInput.value = value;
        }

        ColorPicker.addEventListener('change', (e) => {
            update_color(e.target.value);
            ColorInput.classList.remove('color-picker--invalid');
        });

        ColorInput.addEventListener('blur', (e) => {
            if (isValidHexColor(e.target.value)){
                update_color(e.target.value);
                ColorInput.classList.remove('color-picker--invalid');
            }
            else {
                ColorInput.classList.add('color-picker--invalid');
            }
        });
    });
});
function isValidHexColor(value) {
    return /^#([0-9a-fA-F]{6})$/.test(value);
}