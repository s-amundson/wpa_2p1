"use strict";
var new_family = false;
$(document).ready(function() {
    $("#can-register").hide()
    if ($("#btn-address-edit").attr("family_id") == "") {
        console.log('new family');
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
        console.log($(this).attr("family_id"))
        load_student_family_form($(this).attr("family_id"));
    });

    $("#theme-submit").click(theme_function);

    $("#instructor-form-div").hide();
    $("#btn-instructor").click(function(e) {
        e.preventDefault();
        console.log("show instructor update");
        load_instructor_form();
    });

});


function load_instructor_form() {
    console.log("load instructor form");
    $("#instructor-form-div").show();
    $.get("instructor_update", function(data, status){
        console.log(data);
        $("#instructor-form-div").html(data);
        $("#instructor-info-div").hide();
        $("#instructor_form").submit(function(e) {
            e.preventDefault();
            update_instructor(e);
        });
    });
}

function load_student_family_form(family_id) {
    console.log(family_id)
    $("#student-family-address").hide();
    let url_string = "student_register"
    if (family_id != "") { // if empty new family so load empty form
        url_string = url_string + "/" + family_id + "/";
    }
    console.log(url_string);
    $.get(url_string, function(data, status){
        $("#student-family-form").html(data);
        $("#student-family-form").show();

        $("#family-form").submit(function(e){
            e.preventDefault();
            post_family_function(family_id)
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

async function post_family_function(family_id) {
    console.log('on submit')
    let url_string = "student_family_api";
    if (family_id != "") {
        url_string = url_string + "/" + family_id + "/";
    }
    let data = await $.post(url_string, {
        csrfmiddlewaretoken: $('[name="csrfmiddlewaretoken"]').val(),
        'street': $("#id_street").val(),
        'city' : $("#id_city").val(),
        'state': $("#id_state").val(),
        'post_code': $("#id_post_code").val(),
        'phone': $("#id_phone").val()
    }, function(data, status){
        console.log(data)
        return data;
    }, "json");
    $("#address1").html($("#id_street").val());
    $("#address2").html($("#id_city").val() + " " + $("#id_state").val() + " " + $("#id_post_code").val())
    $("#phone").html($("#id_phone").val())

    $("#student-family-form").html("");
    $("#student-family-form").hide();
    $("#student-family-address").show();
    $("#btn-add-student").prop('disabled', false);
    $("#btn-add-student").show();
    $("#btn-address-edit").attr("family_id", data.id);
    if (url_string == "student_family_api") {
        $("#div-instruct").html("Please enter name and date of birth information for a student");
        load_student_form($("#student_add_div"));
    }
    else {
        $("#div-instruct").html("");
    }
    load_student_table();
    $("#this-student-div").hide();
}

async function theme_function(e) {
    e.preventDefault();
    console.log('theme update')
    console.log($("#id_theme_1").prop('checked'))
    let data = await $.post("theme", {
                csrfmiddlewaretoken: $('[name="csrfmiddlewaretoken"]').val(),
                theme: $("#id_theme_1").prop('checked')});
    if ($("#id_theme_1").prop('checked')) {
        $("#block-main").attr("class", "col-md bg-dark text-white")
    }
    else{
        $("#block-main").attr("class", "col-md bg-light text-dark")
    }

}

async function update_instructor() {
    console.log('update instructor');
    console.log({
        csrfmiddlewaretoken: $("#instructor-form-div").find('[name="csrfmiddlewaretoken"]').val(),
        instructor_expire_date: $("#id_instructor_expire_date").val()
    });
    let data = await $.post("instructor_update", {
        csrfmiddlewaretoken: $("#instructor-form-div").find('[name="csrfmiddlewaretoken"]').val(),
        instructor_expire_date: $("#id_instructor_expire_date").val()
    });
    console.log(data);
    if (data.status == "SUCCESS") {
        $("#instructor-form-div").hide();
        $("#instructor-info-div").show();
        $("#div-instructor_exp_date").html(data.expire_date);
    }
}