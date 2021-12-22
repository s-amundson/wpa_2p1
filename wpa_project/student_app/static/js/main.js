"use strict";
$(document).ready(function(){
    if ($("#alert-message").val() != "") {
        alert($("#alert-message").val());
    }
});

function dob_error(e){
    e.css('border-color', 'red');
    $("#dob-error").html("DOB must be in YYYY-MM-DD Format")
}

function load_student_form(student_div, student_id) {
    console.log(student_id)
    student_div.show();
    $("#btn-add-student").hide()
    var url_string = "add_student"
    if(student_id) {
        url_string = "add_student/" + student_id + "/"
        $("#student-row-" + student_id).hide()
    }
    console.log('load form')
    console.log(url_string)
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
            console.log($(this).val());
            let dob_array = $(this).val().split('-')
            if(dob_array.length != 3) {
                dob_error($(this));
            }
            else if(dob_array[0].length != 4) {
                dob_error($(this));
            }
            else if($(this).val().length != 10) {
                dob_error($(this));
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