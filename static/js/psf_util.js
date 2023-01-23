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
            $("#" + message_id).html(data);
            setTimeout(function() {
                $("#" + message_id).html("");
              }, 2000);
              
        },
        error: function(err) {
            console.log("Updating failed!");
            $("#" + message_id).html("Updating failed!");
            setTimeout(function() {
                $("#" + message_id).html("");
              }, 2000);
        }
    });
}
function psf_vr_selectmenu(id) {
    $("#"+id).selectmenu("menuWidget").menu({
        classes: {
            "ui-menu-item-wrapper": "psf-selectmenu-open-text"
        },
    });
}
