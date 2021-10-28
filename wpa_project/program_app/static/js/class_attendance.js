"use strict";
$.ajaxSetup({traditional: true});
$(document).ready(function(){
    $("#attendance_form").submit(function(e){
        e.preventDefault();
        post_attendance(e);
    });
});

async function post_attendance(e) {
    // to update class attendance
    console.log('on submit');
    let data = {
        csrfmiddlewaretoken: $('#attendance_form [name="csrfmiddlewaretoken"]').val(),
        'attendee_form': $("[name='attendee_form']").val()
    }
    $("#attendance_form :input").each(function() {
        data[$(this).attr('id')] = $(this).prop('checked');
    });
    console.log(data);
    console.log(window.location.href);
    await $.post(window.location.href, data, function(data, status){
        console.log(data);
        return data;
    }, "json");

}