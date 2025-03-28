"use strict";
let policy_string = "";
$(document).ready(function(){
    $("#btn-info-preview").click(function(){
        console.log('preview');
        if($("#id_announcement").length) {
            console.log('anouncement');
            $("#info-preview-container").html($("#id_announcement").val());
        }
        else if($("#id_bio").length) {
            console.log('bio')
            $("#info-preview-container").html($("#id_bio").val());
        }
        else if($("#id_policy").length) {
            policy_string = "";
            if (!$("#id_is_html").prop('checked')) {
                let policy_array = $("#id_policy").val().split("\n");

                policy_array.forEach(function(value) {
                  policy_string += "<p>" + value + "</p>"
                });
            } else {
                policy_string = $("#id_policy").val();
            }

            $("#info-preview-container").html(policy_string);
        }
    });
});