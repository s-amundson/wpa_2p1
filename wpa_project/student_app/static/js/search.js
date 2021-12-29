"use strict";
$(document).ready(function(){
    $("[id^=btn-edit]").click(function(){
        load_student_form($("#student_add_div"), $(this).attr("student-id"));
    });

    $("#btn-address-edit").click(function(){
        console.log($(this).attr("family_id"))
        load_student_family_form($(this).attr("family_id"));
    });
});