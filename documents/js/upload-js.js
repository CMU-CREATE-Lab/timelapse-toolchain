function checkForm(form) // Submit button clicked
{
    //
    // check form input values
    //
    form.submit.disabled = true;
    form.submit.value = "Please wait...";
    document.getElementById('#status').getElementsByTagName('P')[0].className = '';
    return true;
 }

function resetForm(form) // Reset button clicked
{
    form.submit.disabled = false;
    form.submit.value = "Submit";
    document.getElementById('status').getElementsByTagName('P')[0].className = 'hidden';
}


