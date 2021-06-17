"use strict";
$(document).ready(function(){
    $("[id^=btn-edit]").click(function(){
        load_student_form($(this).attr("student-id"));
    });
});