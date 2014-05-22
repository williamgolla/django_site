$(document).ready(function() {
    
    $('#edit').click(function() {
        $('#details').hide();
        $('#edit_details').show();
    });   
    
    $('#cancel').click(function() {
        $('#details').show();
        $('#edit_details').hide();
    });
    
    $('#edit_form').submit(function() {
        $.ajax({
            type: "POST" ,
            url: edit_url ,
            data: $(this).serialize() + "&event_id=" + event_id ,
            success: function(response) {
                if (response.success) {
                    $("#details").load(document.URL + " #details");
                    $("#details").show();
                    $("#edit_details").hide();
                } else if (response.error) {
                    $("#error").html(response.error);
                    $('#details').show();
                    $('#edit_details').hide();
                } else {
                    var errors = jQuery.parseJSON(response);
                    var ret = "";
                    for (var error in errors) {
                        ret += error + ": " + errors[error] + "</br>";
                    }
                    $("#form_errors").html(ret);
                }
            }
        });
        return false;
    });
    
    $('#join').click(function() {
        $.ajax({
            type: "POST" ,
            url: join_url ,
            data: {event_id: event_id } ,
            success: function(response) {
                if (response.success) {
                    $("#success").html(response.success);
                    $("#error").html("");
                    $("#buttons").load(document.URL + " #buttons");
                    $("#participants").load(document.URL + " #participants");
                    $("#owners").load(document.URL + " #owners");
                    $("#changed").load(document.URL + " #changed");
                } else {
                    $("#error").html(response.error);
                    $("#success").html("");
                }
            }
        });
        return false;
    });
    
    $('#leave').click(function() {
        $.ajax({
            type: "POST" ,
            url: leave_url ,
            data: {event_id: event_id } ,
            success: function(response) {
                if (response.success) {
                    $("#success").html(response.success);
                    $("#error").html("");
                    $("#buttons").load(document.URL + " #buttons");
                    $("#participants").load(document.URL + " #participants");
                    $("#changed").load(document.URL + " #changed");
                } else {
                    $("#error").html(response.error);
                    $("#success").html("");
                }
            }
        });
        return false;
    });
    
    $('#delete').click(function() {
        $.ajax({
            type: "POST" ,
            url: delete_url ,
            data: {event_id: event_id } ,
            success: function(response) {
                if (response.success) {
                    $().redirect(event_list, {'msg': 'deleted'});
                } else {
                    $("#error").html(response.error);
                    $("#success").html("");
                }
            }
        });
        return false;
    });
    
    $('.delete_comment').submit(function() {
        $.ajax({
            type: "POST" ,
            url: delete_comment_url ,
            data: $(this).serialize() ,
            success: function(response) {
               if (response.success) {
                    $("#success").html(response.success);
                    $("#error").html("");
                    $("#comm").load(document.URL + " #comm");
                } else {
                    $("#error").html(response.error);
                    $("#success").html("");
                }
            }
        });
        return false;
    });


    $('.promote').submit(function() {
        $.ajax({
            type: "POST" ,
            url: promote_url ,
            data: $(this).serialize() ,
            success: function(response) {
               if (response.success) {
                    $("#success").html(response.success);
                    $("#error").html("");
                    $("#owners").load(document.URL + " #owners");
                    $("#changed").load(document.URL + " #changed");
                } else {
                    $("#error").html(response.error);
                    $("#success").html("");
                }
            }
        });
        return false;
    });


    
    $('.demote').submit(function() {
        $.ajax({
            type: "POST" ,
            url: demote_url ,
            data: $(this).serialize() ,
            success: function(response) {
               if (response.success) {
                    $("#success").html(response.success);
                    $("#error").html("");
                    $("#owners").load(document.URL + " #owners");
                    $("#changed").load(document.URL + " #changed");
                } else {
                    $("#error").html(response.error);
                    $("#success").html("");
                }
            }
        });
        return false;
    });
    
    $('.kick').submit(function() {
        $.ajax({
            type: "POST" ,
            url: kick_url ,
            data: $(this).serialize() ,
            success: function(response) {
               if (response.success) {
                    $("#success").html(response.success);
                    $("#error").html("");
                    $("#participants").load(document.URL + " #participants");
                    $("#owners").load(document.URL + " #owners");
                    $("#changed").load(document.URL + " #changed");
                } else {
                    $("#error").html(response.error);
                    $("#success").html("");
                }
            }
        });
        return false;
    });
});