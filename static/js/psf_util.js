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
function psf_settings_selectmenus(id, addition, message_id,update_val) {
    $("#"+id).selectmenu({
        classes: {
            "ui-selectmenu-open": "psf-selectmenu-open",
        },
    });
    $('#'+id).on('selectmenuselect', function() {
        var val = $("#" + id).val();
        var url_addition = addition + val;
        sendAjax(url_addition, message_id).done(function() {
            settings_vrprot[update_val] = val;
            socket.emit('ex', { id: id, opt: val, fn: "sel" });
            console.log(settings_vrprot)
        }
            ).fail(function() {
                console.log("failed to send");
        });
    });
}

function psf_vr_selectmenu(id) {
    $("#"+id).selectmenu("menuWidget").menu({
        classes: {
            "ui-menu-item-wrapper": "psf-selectmenu-open-text",
        },
    });
};

function psf_write_color_modes_ver() {
    var modes = settings_vrprot.colorModes;
    var active_mode = settings_vrprot.colorMode;
    for (var i = 0; i < modes.length; i++) {
        document.write("<option value=" + modes[i] + ">" + modes[i] + "</option>");
    };
    $("select>option[value='" + active_mode + "']").attr("selected", true);
};
function psf_settings_checkbox(id,message_id,update_val,value,addition,box) {
    if (value == "true") {
        document.getElementById(id).checked = true;
    } else {
        document.getElementById(id).checked = false;
    }
    console.log(document.getElementById(id).checked)
    $('#'+id).change(function() {
        var value = document.getElementById(id).checked;
        var url =  addition + value;
        sendAjax(url, message_id).done(function() {
            settings_vrprot[update_val] = value
            console.log('ex', { id: id, val: $this.is(":checked"), fn: "chk" })
            socket.emit('ex', { id: id, val: $this.is(":checked"), fn: "chk" });
        }
        ).fail(function() {
            document.getElementById(id).checked = value;
        });
    });
    // $("#"+box).click(function() {
    //     $("#"+id).trigger("click");
    // });
};


function psf_write_alphafold_ver() {
    var versions = settings_vrprot.availVer;
    var active_version = settings_vrprot.alphafoldVersion;
    for (var i = 0; i < versions.length; i++) {
        document.write("<option value=" + versions[i] + ">" + versions[i] + "</option>");
    };
    $("select>option[value='" + active_version + "']").attr("selected", true);
};