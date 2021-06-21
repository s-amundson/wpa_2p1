"use strict";
var new_family = false;
$(document).ready(function() {

    $("#can-register").hide()
    if ($("#btn-address-edit").attr("family_id") == "") {
        console.log('new family');
        new_family = true;
        $("#btn-add-student").prop('disabled', true);
        $("#btn-add-student").hide();
        load_student_family_form($("#btn-address-edit").attr("family_id"));
        $("#div-instruct").html("Please enter your address and phone number below");
    }
    else{
        load_student_table();
    }

    $("#btn-add-student").click(function(){
        load_student_form();
    });

    $("#btn-address-edit").click(function(){
        console.log($(this).attr("family_id"))
        load_student_family_form($(this).attr("family_id"));
    });

    $("#theme-submit").click(theme_function);
});

async function add_student_function(student_id) {
    console.log('on submit')
    var url_string = "student_api"
    let getConfirm = false;
    if(student_id) {
        url_string = "student_api/" + student_id + "/";
        $("#student-row-" + student_id).show();
    }
    var of_age = new Date()
    of_age.setFullYear(of_age.getFullYear() - 9)
    console.log(of_age);
    if (Date.parse($("#id_dob").val()) > of_age) {
        getConfirm = confirm("Students under the age of 9 are not permitted to participate in classes.\n"
          +  "Do you wish to continue to add this student?");
    }
    else {
        getConfirm = true;
    }
    console.log(url_string);
    if (getConfirm) {
        let data = await $.post(url_string, {
                csrfmiddlewaretoken: $('[name="csrfmiddlewaretoken"]').val(),
                'first_name': $("#id_first_name").val(),
                'last_name' : $("#id_last_name").val(),
                'dob': $("#id_dob").val()
            }, function(data, status){
                console.log(data)
                return data;
                }, "json");
        $("#student_add_div").hide();
        $("#btn-add-student").show();
        $("#div-instruct").html("");
        load_student_table();
    }
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
    $.get("student_table", function(data, status){
        $("#student-table-div").html(data);

        if($(".student_row").length == 0) {
            //  no students therefore we need to load the student form
            load_student_form();
            $("#can-register").hide()
        }
        else {
            $("[id^=btn-edit]").click(function(){
                load_student_form($(this).attr("student-id"));
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
        load_student_form();
    }
    else {
        $("#div-instruct").html("");
    }
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