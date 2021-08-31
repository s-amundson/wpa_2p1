"use strict";
var report_owners = ['president', 'vice', 'secretary', 'treasure'];
var report_count = 0;
$(document).ready(function() {
    // if meeting has started display time started. else put button to start meeting.
    if ($("#id_start_time").val() == "") {
        $("#id_start_time").parent().html($("#id_start_time").parent().html() + $("#div-start-btn").html());
        $("#div-start-btn").html('')
        $("#id_start_time").hide();
        $("#minutes-form :input").each(disable_inputs)
    }
    else {
        $("#btn-start").hide();
    }

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
        index_business_div($(this));
    });

    // add listener to the new business button
    $("#btn-new-business").click(function(e){
        e.preventDefault();
        load_business_form();
//        load_report_form($("#div-treasure"), 'treasure');
    });
});

function disable_inputs() {
    let arr = ['id_meeting_date', 'btn-start', 'id_attending'];
    if ($.inArray($(this).prop('id'), arr) == -1) {
        $(this).prop('disabled', true);
    }
}
function index_business_div(container) {
    report_count = report_count + 1;
    container.find("#business_business").attr("count", report_count)
    container.find("#business_business").prop('id', "business_business-" + report_count);
    container.find("#business_minutes").prop('id', "business_minutes-" + report_count);
    container.find("#business_added_date").prop('id', "business_added_date-" + report_count);
    container.find("#business_resolved").prop('id', "business_resolved-" + report_count);
    container.find("#business-id").prop('id', "business-id-" + report_count);
    container.prop('id', "business-div-" + report_count);
    $("#business_business-" + report_count).change(function(e){
        e.preventDefault();
        console.log($(this));
        save_business($(this));
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

async function load_business_form() {
    await $.get($("#url-business").val(), function(data, status){
        console.log(data);
        $("#div-new-business").html($("#div-new-business").html() + data);

        let count = parseInt($("#new-business-count").val()) + 1
        $("#new-business-count").val(count)
        $("#business_minutes").val($("#minutes-id").val());
        index_business_div($("#div-new-business").find("#business-div"))
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
    let url_string = $("#url-business").val()
    if ($("#business-id-" + count).val() != "None") {
        url_string = url_string + "/" + $("#business-id-" + count).val()
    }
    console.log($("#business-div-" + count).find('[name="csrfmiddlewaretoken"]').val())
    await $.post(url_string, {
        csrfmiddlewaretoken: $("#business-div-" + count).find('[name="csrfmiddlewaretoken"]').val(),
//                disabled_fields = ['added_date']
//        hidden_fields = ['minutes']
//        optional_fields = ['business', '']
        added_date: $("#business_owner-" + count).val(),
        minutes: $("#business_minutes-" + count).val(),
        business: business_element.val(),
        resolved: $("#business_resolved-" + count).prop('checked'),
    }, function(data, status){
        console.log(data);
        $("#business-id-" + count).val(data.report_id);
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
    }, "json");

}
