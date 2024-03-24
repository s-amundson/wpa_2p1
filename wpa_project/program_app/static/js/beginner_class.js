"use strict";

$(document).ready(function(){
    var beginner_default = $("#id_beginner_limit").val()
    var return_default = $("#id_returnee_limit").val()

    $("#id_class_type").change(function(e){
        console.log($(this).val())
        if ($(this).val() == 'beginner') {
            $("#id_returnee_limit").val(0);
            $("#id_returnee_wait_limit").val(0);
            if ($("#id_beginner_limit").val() == 0) {
                $("#id_beginner_limit").val(beginner_default);
            }
        }
        else if ($(this).val() == 'returnee') {
            $("#id_beginner_limit").val(0);
            $("#id_beginner_wait_limit").val(0);
            if ($("#id_returnee_limit").val() == 0) {
                $("#id_returnee_limit").val(return_default);
            }
        }
        else {
            if ($("#id_beginner_limit").val() == 0) {
                $("#id_beginner_limit").val(beginner_default);
            }
            if ($("#id_returnee_limit").val() == 0) {
                $("#id_returnee_limit").val(return_default);
            }
        }
    });
    $("#id_state").change(function(e){
        if ($(this).val() == 'canceled') {
            alert_notice("Warning", "Setting the state to canceled will cause a refund to go out to all students.");
        }
    });
});