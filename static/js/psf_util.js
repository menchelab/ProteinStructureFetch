function sendAjax(url_addition, message_id) {
    var base_url = "http://" + window.location.href.split("/")[2];
    var url = base_url + url_addition;
    console.log(url)
    return $.ajax({
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
            console.log(err);
            $("#" + message_id).html("Updating failed!");
            setTimeout(function() {
                $("#" + message_id).html("");
              }, 5000);
        }
    });
}
function psf_vr_selectmenu(id) {
    $("#"+id).selectmenu("menuWidget").menu({
        classes: {
            "ui-menu-item-wrapper": "psf-selectmenu-open-text"
        },
    });
};

function psr_write_color_modes_ver() {
    var modes = settings.colorModes;
    var active_mode = settings.mode;
    for (var i = 0; i < modes.length; i++) {
        document.write("<option value=" + modes[i] + ">" + modes[i] + "</option>");
    };
    $("select>option[value='" + active_mode + "']").attr("selected", true);
};
function psf_check_overwrite() {
    var overwrite = settings.overwrite;
    if (overwrite == "true") {
        document.getElementById("psf_overwrite").checked = true;
    } else {
        document.getElementById("psf_overwrite").checked = false;
    }
    console.log( document.getElementById("psf_overwrite").checked)
};


function psf_write_alphafold_ver() {
    var versions = settings.availVer;
    var active_version = settings.currVer;
    for (var i = 0; i < versions.length; i++) {
        document.write("<option value=" + versions[i] + ">" + versions[i] + "</option>");
    };
    $("select>option[value='" + active_version + "']").attr("selected", true);
};