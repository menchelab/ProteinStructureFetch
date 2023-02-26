function sendAjax(url_addition, message_id, doneFunction, failFunction) {
  var base_url = "http://" + window.location.href.split("/")[2];
  var url = base_url + url_addition;
  console.log(url);
  $.ajax({
    type: "POST",
    url: url,
    cache: false,
    contentType: false,
    processData: false,
    success: function (data) {
      setStatus("success", message_id, data);
      if (doneFunction != undefined) {
        doneFunction();
      }
    },
    error: function (err) {
      setStatus("error", message_id, "Updating failed!");
      if (failFunction != undefined) {
        failFunction();
      }
    },
  });
}
function psf_settings_selectmenus(id, addition, message_id, update_val) {
  $("#" + id).selectmenu({
    classes: {
      "ui-selectmenu-open": "limited-selectmenu-open",
    },
  });
  $("#" + id).on("selectmenuselect", function () {
    var val = $("#" + id).val();
    var url_addition = addition + val;
    function doneFunction() {
      settings_vrprot[update_val] = val;
      socket.emit("ex", { id: id, opt: val, fn: "sel" });
      console.log(settings_vrprot);
    }
    function failFunction() {
      console.log("failed to send");
    }
    sendAjax(url_addition, message_id, doneFunction, failFunction);
  });
}

function psf_vr_selectmenu(id) {
  $("#" + id)
    .selectmenu("menuWidget")
    .menu({
      classes: {
        "ui-menu-item-wrapper": "limited-selectmenu-open-text",
      },
    });
}

function psf_write_color_modes_ver() {
  var modes = settings_vrprot.colorModes;
  var active_mode = settings_vrprot.colorMode;
  for (var i = 0; i < modes.length; i++) {
    document.write("<option value=" + modes[i] + ">" + modes[i] + "</option>");
  }
  $("select>option[value='" + active_mode + "']").attr("selected", true);
}
function psf_settings_checkbox(
  id,
  message_id,
  update_val,
  value,
  addition,
  box
) {
  console.log(value);
  if (value.toString().toLowerCase() == "true") {
    document.getElementById(id).checked = true;
  } else {
    document.getElementById(id).checked = false;
  }
  console.log(document.getElementById(id).checked);
  $("#" + id).change(function () {
    var value = document.getElementById(id).checked;
    var url = addition + value;
    sendAjax(url, message_id)
      .done(function () {
        settings_vrprot[update_val] = value;
        console.log("ex", {
          id: id,
          val: $("#" + id).is(":checked"),
          fn: "chk",
        });
        socket.emit("ex", {
          id: id,
          val: $("#" + id).is(":checked"),
          fn: "chk",
        });
      })
      .fail(function () {
        document.getElementById(id).checked = value;
      });
  });
  // $("#"+box).click(function() {
  //     $("#"+id).trigger("click");
  // });
}

function psf_write_alphafold_ver() {
  var versions = settings_vrprot.availVer;
  var active_version = settings_vrprot.alphafoldVersion;
  for (var i = 0; i < versions.length; i++) {
    document.write(
      "<option value=" + versions[i] + ">" + versions[i] + "</option>"
    );
  }
  $("select>option[value='" + active_version + "']").attr("selected", true);
}
