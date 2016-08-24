var rootURL = "http://www.create.maps.org/projects/";
var firstEnter = true;
var lastGeneratedID = "";
var checkUrlTimer = null;
var urlAvailable = false;

function checkForm(form) // Submit button clicked
{
    //
    // check form input values
    //
    var $input = $('input[name=project_title]');
    $input.val($input.val().trim());
    $input = $('input[name=project_id]');
    $input.val($input.val().trim());
    $input = $('input[name=email]');
    $input.val($input.val().trim());

    if(!$('input[name=csv_file]').val()){
        $('#status').html("<p><span style='color:red'>No File:</span> Please select a file and submit again.</p>");
        $('input[name=csv_file]').focus();
        return false;
    }
    if(!$('input[name=project_title]').val()){
        $('#status').html("<p><span style='color:red'>No Project Name:</span> Please enter a project name and submit again.</p>");
        $('input[name=project_title]').focus();
        return false;
    }
    if(!$('input[name=project_id]').val()){
        $('#status').html("<p><span style='color:red'>No Project ID:</span> Please enter a project ID and submit again.</p>");
        $('input[name=project_id]').focus();
        return false;
    }
    if(!validateUrl($('input[name=project_id]').val())){
        $('#status').html("<p><span style='color:red'>Invalid Project ID:</span> Please correct the Project ID and submit again.</p>");
        $('input[name=project_id]').focus();
        return false;
    }
    if(!$('input[name=email]').val()){
        $('#status').html("<p><span style='color:red'>No Email:</span> Please enter an email and submit again.</p>");
        $('input[name=email]').focus();
        return false;
    }
    if(!urlAvailable){
        $('#status').html("<p><span style='color:red'>URL Unavailable</span> Please enter another project ID and submit again.</p>");
        $('input[name=project_id]').focus();
        return false;
    }

    form.submit.disabled = true;
    form.submit.value = "Please wait...";
    $('#status').html("<p><span style='color:green'>Uploading CSV File, wait for redirect...</span></p>"+ 
                      "<p>This may take a while for large files.</p>");

    return true;
 }

function resetForm(form) // Reset button clicked
{
    urlAvailable = false;
    clearTimeout(checkUrlTimer);
    form.submit.disabled = false;
    form.submit.value = "Submit";
    $('#example-url span').text('e.g. ' + rootURL + 'my-projects-title');
    $('#valid-url')[0].className = 'validate'
    $('#available-url')[0].className = 'validate';
}

function generateProjectID(value){
    firstEnter = false;
    var project_id = encodeURIComponent(
        value.toLowerCase().trim().replace(/[^a-zA-Z0-9 ]/g, "").replace(/\s/g, '-'));
    if($('input[name=project_id]').val() == lastGeneratedID || !$('input[name=project_id]').val() || firstEnter){
        $('input[name=project_id]').val(project_id);
        validateID(project_id);
    }

    lastGeneratedID = project_id;
}

function validateID(value){
    if(value){
        $('#example-url span').text('e.g. ' + rootURL + value);
        var validURL = validateUrl(value.trim());
        $('#valid-url')[0].className = validURL ? 'validate valid' : 'validate invalid';
        if(validURL){
            urlAvailable = false;
            $('#available-url')[0].className = 'validate';
            clearTimeout(checkUrlTimer);
            checkUrlTimer = setTimeout(function(){
                checkUrl(rootURL+$('input[name=project_id]').val());
            }, 200);
        }else{
            $('#available-url')[0].className = 'validate';
            clearTimeout(checkUrlTimer);
        }
    }else{
        urlAvailable = false;
        clearTimeout(checkUrlTimer);
        $('#example-url span').text('e.g. ' + rootURL + 'my-projects-title');
        $('#valid-url')[0].className = 'validate'
        $('#available-url')[0].className = 'validate';
    }
}

function validateUrl(url){
    return encodeURIComponent(url) == url;
}

function checkUrl(url){
    var request = new XMLHttpRequest;
    request.open('HEAD', url, true);
    request.send();
    request.onreadystatechange = function(){
        var available = !(request.status==200);
        $('#available-url')[0].className = available ? 'validate valid' : 'validate invalid';
        urlAvailable = available;
    }
};



