"use strict";
$.ajaxSetup({traditional: true});
$(document).ready(function(){
    $(".attend-check").change(function(e){
        let data = {
            'csrfmiddlewaretoken': $('#attendance_form [name="csrfmiddlewaretoken"]').val(),
        }
        data[$(this).attr('id')] = $(this).prop('checked');
        post_attend($(this).attr('attend_url'), data);
    });
});

async function post_attend(url, send_data) {
    await $.post(url, send_data, function(data, status){
        return data;
    }, "json");
}
