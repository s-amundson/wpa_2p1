"use strict";
$(document).ready(function() {
    console.log('page loaded');
    $("#can-register").hide()
    if ($("#btn-address-edit").attr("family_id") == "") {
        console.log('new family');
        $("#btn-add-student").prop('disabled', true);
        load_student_family_form($("#btn-address-edit").attr("family_id"));
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
});

async function add_student_function(student_id) {
    console.log('on submit')
    var url_string = "student_api"
    if(student_id) {
        url_string = "student_api/" + student_id + "/";
        $("#student-row-" + student_id).show();
    }
    console.log(url_string);
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
    load_student_table();
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
            load_add_student_form();
            $("#can-register").hide()
        }
        else {
            $("[id^=btn-edit]").click(function(){
                load_student_form($(this).attr("student-id"));
            });
            $("#can-register").show()
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
    $("#btn-address-edit").attr("family_id", data.id)
}
