$(document).ready(function() {
    $("#searchUsers").click(function() {
        var url = "/users/";
        var name = $("#searchN").val();
        if (name != ""){
            name = "n=" + name + "/";
        }
        var loc = $("#searchL").val();
        if (loc != "") {
            loc = "l=" + loc + "/";
        }
        var link = url+name+loc;
        window.location.href = link;
    });
    $("#searchEvents").click(function() {
        var url = "/events/";
        var name = $("#searchN").val();
        if (name != ""){
            name = "n=" + name + "/";
        }
        var loc = $("#searchL").val();
        if (loc != "") {
            loc = "l=" + loc + "/";
        }
        var link = url+name+loc;
        window.location.href = link;    });
});