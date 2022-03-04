"use strict";
var edit_class_id = null;
$(document).ready(function(){
    $("#session-form").submit(function(e){
        if (session_id != null){
            e.preventDefault();
            post_session();
        }
    });
    $("#btn-add-class").click(function() {
        $(this).hide();
        load_joad_class_form(null);
    });
    if (class_list_url != null) {
        edit_btn();
        load_class_table();
    }

    $(".attend-check").change(function(e){
        let data = {
            'csrfmiddlewaretoken': $('[name="csrfmiddlewaretoken"]').val(),
        }
        data[$(this).attr('id')] = $(this).prop('checked');
        post_attend($(this).attr('attend_url'), data);
    });

    console.log($("#joad-event-div").length)
    if ($("#joad-event-div").length) {
        $.get(joad_event_list_url, function(data, status){
            $("#joad-event-div").html(data)
        });
    }

});

function class_url(class_id=null) {
    console.log(class_id);
    if(class_id == null) {
        return joad_class_url;
        url_string = url_string + 'class_id';
    }
    console.log(joad_class_url + class_id);
    return joad_class_url + class_id + '/';
}

function edit_btn(){
    $(".edit-class").click(function() {
        edit_class_id = $(this).attr("class_id");
        console.log(edit_class_id);
        $(this).parents("tr").remove();
        $("#btn-add-class").hide();
        load_joad_class_form(edit_class_id);
    });
}

function load_class_table(){
    $.get(class_list_url + session_id + '/', function(data, status){
        $("#class-table-div").html(data);
        edit_btn();
    });
}

function load_joad_class_form(class_id) {
    $.get(class_url(class_id), function(data, status){
        $("#jc-form").html(data);
        $("#joad-class-form").submit(function(e){
            e.preventDefault();
            post_joad_class_form();
        });
        $("#id_session").val(session_id)
    });
}

async function post_attend(url, send_data) {
    await $.post(url, send_data, function(data, status){
        return data;
    }, "json");
}

async function post_joad_class_form() {
    $("#id_session").prop('disabled', false);
    let form_data = objectifyForm($("#joad-class-form").serializeArray());
    let data = await $.post(class_url(edit_class_id), form_data, function(data, status){
        console.log(data);
        if(data['success']) {
            load_class_table();
//            $("#class-list-body").append("<tr><td>" + data['id'] + "</td><td>" + data['class_date'] + "</td><td>" +
//                data['state'] + '</td><td><button class="btn btn-primary edit-class" type="button" class_id="' +
//                data['id'] + '"> Update </button></td></tr>')
        }
        else {
            alert_notice("Error", "Error with form")
        }
    }, "json");
    edit_class_id = null;
    $("#btn-add-class").show();
    $("#joad-class-form").hide();
    edit_btn();
}

async function post_session() {
    let form_data = $("#session-form").serializeArray();
    form_data = objectifyForm(form_data);

    console.log(form_data);
    let url_string = session_url;
    let data = await $.post(url_string, form_data, function(data, status){
        console.log(data);
        console.log(status);
        alert_notice("Submitted", status)
        return data;
    }, "json");
    session_id = data["session_id"];

}
