"use strict";
var new_family = false;
$(document).ready(function() {
    $("#can-register").hide()
    if ($("#btn-address-edit").attr("family_id") == "") {
        $(".can-register-top").hide();
        new_family = true;
        $("#btn-add-student").prop('disabled', true);
        $("#btn-add-student").hide();
        if ($("#this-student").val() == 'None') {
            $("#btn-address-edit").prop('disabled', true);
            load_student_form($("#this-student-div"));
            $("#div-instruct").html("Please enter your name and date of birth below");
        }
        else {
            load_student_family_form($("#btn-address-edit").attr("family_id"));
            $("#div-instruct").html("Please enter your address and phone number below");
        }
    }
    else{
        load_student_table();

    }

    $("#btn-add-student").click(function(){
        load_student_form($("#student_add_div"));
    });

    $("#btn-address-edit").click(function(){
        load_student_family_form($(this).attr("family_id"));
    });

    $("#instructor-form-div").hide();
    $("#btn-instructor").click(function(e) {
        e.preventDefault();
        console.log("show instructor update");
        load_instructor_form();
    });

});


function load_instructor_form() {
    $("#instructor-form-div").show();
    $.get(url_instructor_update, function(data, status){
        $("#instructor-form-div").html(data);
        $("#instructor-info-div").hide();
        $("#instructor_form").submit(function(e) {
            e.preventDefault();
            update_instructor(e);
        });
    });
}


function load_student_table() {
    $.get(student_table_url, function(data, status){
        $("#student-table-div").html(data);

        if($(".student_row").length == 0) {
            //  no students therefore we need to load the student form
            load_student_form($("#student_add_div"));
            $("#can-register").hide()
        }
        else {
            $("[id^=btn-edit]").click(function(){
                load_student_form($("#student_add_div"), $(this).attr("student-id"));
            });
            if (new_family){
                $("#can-register").show()
            }
        }
    });
}

async function update_instructor() {
    console.log('update instructor');
    let data = await $.post(url_instructor_update, $("#instructor_form").serializeArray());
    if (data.status == "SUCCESS") {
        $("#instructor-form-div").hide();
        $("#instructor-info-div").show();
        $("#instructor_exp_date").html(data.expire_date);
        $("#instructor_level").html(data.level);
    }
}