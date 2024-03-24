"use strict";

$(document).ready(function() {
    $("#id_state").change( function() {
        if ($(this).val() == 'canceled') {
            $("#cancel-preview").show();
            $("#id_cancel_message").show();
            $("label[for=id_cancel_message").show();
        } else {
            $("#cancel-preview").hide();
            $("#id_cancel_message").hide();
            $("label[for=id_cancel_message").hide();
        }
    });
    $("#id_cancel_message").keyup(function() {
        $("#message-insert").html($("#id_cancel_message").val())
    });
    $("#cancel-preview").hide();
    $("#id_cancel_message").hide();
    $("label[for=id_cancel_message").hide();
});

