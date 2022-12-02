function sendAjax(url_addition, message_id) {
    var base_url = "http://" + window.location.href.split("/")[2];
    var url = base_url + url_addition;
    $.ajax({
        type: "POST",
        url: url,
        cache: false,
        contentType: false,
        processData: false,
        success: function(data) {
            $("#"+message_id).html(data);
        },
        error: function(err) {
            console.log("Updating failed!");
            $("#"+message_id).html("Updating failed!");
        }
    });
}