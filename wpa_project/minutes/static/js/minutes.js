"use strict";
var report_owners = ['president', 'vice', 'secretary', 'treasure'];
var report_count = 0;
$(document).ready(function() {
    // if meeting has started display time started. else put button to start meeting.
    if ($("#id_start_time").val() == "") {
        $("#id_start_time").hide();
        $("#minutes-form :input").each(function() {
            disable_inputs(true);
        });
    }
    else {
        $("#btn-start").hide();
    }
    $("#btn-start").click(function(e){
        e.preventDefault();
        disable_inputs(false);
        $("#minutes-form").submit();
    });

    // loop though the report owners
    $.each(report_owners, function(index, value) {
        // loop though the existing reports and update indexes and set event
        $("#div-" + value).find(".report-div").each(function(index) {
            index_report_div($(this))
        });

        // add listener to the report buttons
        $("#btn-" + value + "-report").click(function(e){
            e.preventDefault();
            load_report_form($("#div-" + value), value);
        });
    });

    // index old business
    $("#div-old-business").find(".business-div").each(function(index) {
        index_business_div($(this), false);
    });

    // index new business
    $("#div-new-business").find(".business-div").each(function(index) {
        index_business_div($(this), true);
    });

    // add listener to the new business button
    $("#btn-new-business").click(function(e){
        e.preventDefault();
        load_business_form();
    });
});

function disable_inputs(state) {
    let arr = ['id_meeting_date', 'btn-start', 'id_attending'];
    if ($.inArray($(this).prop('id'), arr) == -1) {
        $(this).prop('disabled', state);
    }
}

function get_time() {
    var dt = new Date();
    return dt.getHours() + ":" + dt.getMinutes() + ":" + dt.getSeconds();
}

function index_business_div(container, new_business) {
    report_count = report_count + 1;

    container.attr("new-business", new_business)
    container.find("#business_business").attr("count", report_count)
    container.find("#business_business").prop('id', "business_business-" + report_count);
    container.find("#business_minutes").prop('id', "business_minutes-" + report_count);
    container.find("#business_added_date").prop('id', "business_added_date-" + report_count);
    container.find("#business_resolved").prop('id', "business_resolved-" + report_count);
    container.find(".business-id").prop('id', "business-id-" + report_count);
    container.find("#btn-add-update").attr("count", report_count)
    container.find("#btn-add-update").prop('id', "btn-add-update-" + report_count);
    if(container.find("#business_resolved_bool").prop('checked')) {
        $("#business_business-" + report_count).prop('disabled', true);
    }
    container.find("#business_resolved_bool").attr("count", report_count)
    container.find("#business_resolved_bool").prop('id', "business_resolved_bool-" + report_count);
    container.find("#div-resolved-date").prop('id', "div-resolved-date-" + report_count);
    container.prop('id', "business-div-" + report_count);

    container.find(".div-business-update").each(function(index) {
        index_update($(this), false)
    });

    if (new_business) {
        $("#btn-add-update-" + report_count).hide()
    }
    else {
        container.find("#business_business-" + report_count).prop('disabled', true);
    }

    $("#business_business-" + report_count).change(function(e){
        console.log($(this));
        save_business($(this));
    });

    console.log("#business_resolved_bool-" + report_count)
    $(".resolved-check").change(function(e){
        console.log("resolved check")
        console.log($(this).attr("count"));
        save_business($("#business_business-" + $(this).attr("count")));
    });

    $("#btn-add-update-" + report_count).click(function(e){
        e.preventDefault();
        console.log($(this).attr("count"));
        load_business_update($("#business-id-" + $(this).attr("count")).val());
    });
}

function index_report_div(container) {
    report_count = report_count + 1;
    container.find("#report_report").attr("count", report_count)
    container.find("#report_owner").prop('id', "report_owner-" + report_count);
    container.find("#report_minutes").prop('id', "report_minutes-" + report_count);
    container.find("#report_report").prop('id', "report_report-" + report_count);
    container.find("#report-id").prop('id', "report-id-" + report_count);
    container.prop('id', "report-div-" + report_count);
    $("#report_report-" + report_count).change(function(e){
            e.preventDefault();
            console.log($(this));
            save_report($(this));
        });
}

function index_update(container, new_update) {
    report_count = report_count + 1;

    container.attr("new-business", new_update)
    container.find("#business-update-id").prop('id', "business-update-id-" + report_count);
    container.find("#update_business").prop('id', "update_business-" + report_count);
    container.find("#update_update_text").attr("count", report_count);
    container.find("#update_update_text").prop('id', "update_update_text-" + report_count);
    container.find("#update_update_date").prop('id', "update_update_date-" + report_count);
    $("#update_update_text-" + report_count).change(function(e){
        console.log($(this));
        save_update($(this));
    });
}

function indicate_saved(status) {
    // show user that the information was saved or error
    if (status) {
        $("#div-saved-message").html("Saved at:" + get_time());
    }
    else {
        alert('save error')
    }
}

async function load_business_form() {
    await $.get($("#url-business").val(), function(data, status){
        $("#div-new-business").html($("#div-new-business").html() + data);
        $("#business_minutes").val($("#minutes-id").val());
        index_business_div($("#div-new-business").find("#business-div"), true)
    });
}

async function load_business_update(business) {
    console.log(business)
    await $.get($("#url-business-update").val(), function(data, status){
        console.log(status);
        $("#div-business-update").html($("#div-business-update").html() + data);
        $("#div-business-update").find("#update_business").val(business);
        index_update($("#div-business-update"), true)
    });
}

async function load_report_form(container, owner) {
    await $.get($("#url-report").val(), function(data, status){
//        console.log(data);
        container.html(container.html() + data);
        report_count = report_count + 1;
//        let count = parseInt(container.find(".report-count").val()) + 1
        container.find(".report-count").val(report_count)
        $("#report_owner").val(owner);
        $("#report_minutes").val($("#minutes-id").val());
        index_report_div(container)

    });
}

async function save_business(business_element) {
    let count = business_element.attr('count')
    console.log(count)
    console.log($("#business-id-" + count).val())
    let url_string = $("#url-business").val()
    if ($("#business-id-" + count).val() != "None") {
        url_string = url_string + "/" + $("#business-id-" + count).val()
    }
    console.log($("#business-div-" + count).find('[name="csrfmiddlewaretoken"]').val())

    await $.post(url_string, {
        csrfmiddlewaretoken: $("#business-div-" + count).find('[name="csrfmiddlewaretoken"]').val(),
        added_date: $("#business_owner-" + count).val(),
        minutes: $("#business_minutes-" + count).val(),
        business: business_element.val(),
        resolved_bool: $("#business_resolved_bool-" + count).prop('checked'),
    }, function(data, status){
        console.log(data);
        $("#business-id-" + count).val(data.business_id);
        indicate_saved(data.success)
        if ($("#business-div-" + count).attr('new-business')) {
                $("#business-div-" + count + " :input").each( function() {
                $(this).prop('disabled', data.success);
            });
        }
        else {
            $("#business-div-" + count).find(".div-business-update").each(function(index) {
                logging.debug($(this).attr('new-update'))

            });
        }

        $("#business_resolved_bool-" + count).prop('disabled', false);
    }, "json");
}

async function save_report(report_element) {
    let count = report_element.attr('count')
    console.log(count)
    console.log($("#report-id-" + count));
    let url_string = $("#url-report").val()
    if ($("#report-id-" + report_element.attr('count')).val() != "None") {
        url_string = url_string + "/" + $("#report-id-" + report_element.attr('count')).val()
    }
    console.log($("#report-div-" + count).find('[name="csrfmiddlewaretoken"]').val())
    await $.post(url_string, {
        csrfmiddlewaretoken: $("#report-div-" + count).find('[name="csrfmiddlewaretoken"]').val(),
        owner: $("#report_owner-" + count).val(),
        minutes: $("#report_minutes-" + count).val(),
        report: report_element.val()
    }, function(data, status){
        console.log(data);
        $("#report-id-" + count).val(data.report_id);
        indicate_saved(data.success);
    }, "json");
}

async function save_update(update_element) {
    let count = update_element.attr('count')
    console.log(count)
    let url_string = $("#url-business-update").val()
    if ($("#business-update-id-" + update_element.attr('count')).val() != "None") {
        url_string = url_string + "/" + $("#business-update-id-" + update_element.attr('count')).val()
    }
    console.log($("#business-update-id-" + count).prev('[name="csrfmiddlewaretoken"]').val())
    await $.post(url_string, {
        csrfmiddlewaretoken: $("#business-update-id-" + count).prev('[name="csrfmiddlewaretoken"]').val(),
        business: $("#update_business-" + count).val(),
        update_text: update_element.val()
    }, function(data, status){
        console.log(data);
        if (status == 'success') {
            $("#div-saved-message").html("Saved at:" + get_time());
        }
        $("#business-update-id-" + count).val(data.update_id);
        indicate_saved(data.success);
    }, "json");
}
