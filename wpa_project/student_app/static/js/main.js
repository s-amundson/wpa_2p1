"use strict";
$(document).ready(function(){
    if ($("#alert-message").val() != "") {
        alert($("#alert-message").val());
    }
});

async function add_student_function(student_id) {
    var url_string = "student_api"
    let getConfirm = false;
    if(student_id) {
        url_string = "student_api/" + student_id + "/";
        $("#student-row-" + student_id).show();
    }
    var of_age = new Date()
    of_age.setFullYear(of_age.getFullYear() - 9)
    if (Date.parse($("#id_dob").val()) > of_age) {
        getConfirm = confirm("Students under the age of 9 are not permitted to participate in classes.\n"
          +  "Do you wish to continue to add this student?");
    }
    else {
        getConfirm = true;
    }
    if (getConfirm) {
        let student_info = {
                csrfmiddlewaretoken: $('[name="csrfmiddlewaretoken"]').val(),
                'first_name': $("#id_first_name").val(),
                'last_name' : $("#id_last_name").val(),
                'dob': $("#id_dob").val(),
                'email': $("#id_email").val()
            }
        if ($("#student_form").find("#id_safety_class").length == 1) {
            student_info['safety_class'] = $("#id_safety_class").val()
        }
        let data = await $.post(url_string, student_info, function(data, status){
                return data;
                }, "json");
        $("#student_add_div").hide();

        if ('error' in data) {
            Object.entries(data["error"]).forEach(([key, value]) => {
               alert(value[0])
            });
        }
        else {
            if ($("#this-student").val() == 'None') {
                $("#btn-address-edit").prop('disabled', false);
                $("#this-student").val(data.id)
                $("h2").html(data.first_name + data.last_name + "'s Profile Page")
                $("#btn-student-form-add").hide();
            }

            if ($("#btn-address-edit").attr("family_id") == "") {
                load_student_family_form($("#btn-address-edit").attr("family_id"));
                $("#div-instruct").html("Please enter your address and phone number below");
            }
            else {
                $("#btn-add-student").show();
                $("#div-instruct").html("");
            }
            try {
                load_student_table();
            } catch (e) {
            }
        }
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

function load_student_form(student_div, student_id) {
    student_div.show();
    $("#btn-add-student").hide()
    var url_string = "add_student"
    if(student_id) {
        url_string = "add_student/" + student_id + "/"
        $("#student-row-" + student_id).hide()
    }
    $.get(url_string, function(data, status){
//        $("#student_add_div").html(data);
        student_div.html(data);
        if(student_id) {
            $("#btn-student-form-add").html("Update")
        }
        else {
            $("#btn-student-form-add").html("Add")
        }
        $("#student_form").submit(function(e){
            e.preventDefault();
            add_student_function(student_id)
            try {
                load_student_table();
            } catch (e) {
            }
        });
        $("#btn-student-form-close").click(function() {
            student_div.html("");
            try {
                load_student_table();
            } catch (e) {
            }
        });
        $("#id_dob").change(function() {
            let dob_array = $(this).val().split('-')
            let is_valid = true;
            if(dob_array.length != 3) {
                is_valid = false;
            }
            else if(dob_array[0].length != 4) {
                is_valid = false;
            }
            else if($(this).val().length != 10) {
                is_valid = false;
            }
            if (is_valid) {
                $(this).css('border-color', 'blue');
                $("#dob-error").hide();
            }
            else {
                $(this).css('border-color', 'red');
                $("#dob-error").html("DOB must be in YYYY-MM-DD Format");
                $("#dob-error").show();
            }
        });
    });
}
// Pad a number with leading zeros from Geeksforgeeks.org
function pad(n, width) {
    n = n + '';
    return n.length >= width ? n :
        new Array(width - n.length + 1).join('0') + n;
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

    try {
        load_student_table();
    } catch (e) {
    }

    $("#this-student-div").hide();
    $(".can-register-top").show();
}