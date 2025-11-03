document.addEventListener('DOMContentLoaded', function() 
{
    const visibilityField = document.querySelector('#id_visibility');
    const passwordField = document.querySelector('#id_password');
  
    function togglePasswordField() {
        if (visibilityField.value === 'protected') 
        {
            passwordField.parentElement.style.display = '';
        }
        else
        {
            passwordField.parentElement.style.display = 'none';
        }
    }
  
    visibilityField.addEventListener('change', togglePasswordField);
    togglePasswordField();
});

