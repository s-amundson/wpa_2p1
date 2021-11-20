"use strict";
$(document).ready(function(){
    $("[id^=btn-edit]").click(function(){
        load_student_form($("#student_add_div"), $(this).attr("student-id"));
    });
});