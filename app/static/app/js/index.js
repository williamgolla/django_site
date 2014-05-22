$(document).ready(function() {
    $('#login').submit(function() {
        $.ajax({
            type: "POST" ,
            url: login_url ,
            data: $(this).serialize() ,
            success: function(response) {
                if (response.redirect) {
                    window.location.replace(response.redirect);
                } else {
                    $("#error").html(response.error);
                    $("#success").html("");
                }
            }
        });
        return false;
    });
});