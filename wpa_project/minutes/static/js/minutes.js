"use strict";
var report_owners = ['president', 'vice', 'secretary', 'treasure'];

$(document).ready(function() {
    // if meeting has started display time started. else put button to start meeting.
    if ($("#id_start_time").val() == "") {
        $("#id_start_time").hide();
    }
    else {
        $("#btn-start").hide();
    }
    $("#btn-start").click(function(e){
        e.preventDefault();
        disable_inputs(false);
        $("#minutes-form").submit();
        $(".btn-report").prop('disabled', false);
    });

    if ($("#id_end_time").val() == "") {
        $("#id_end_time").hide();
    }
    else {
        $("#btn-end").hide();
    }
    $("#btn-end").click(function(e){
        e.preventDefault();
        $("#id_end_time").val(get_time)
        disable_inputs(false);
        $("#minutes-form").submit();
        $(".btn-report").prop('disabled', false);
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

    $(".btn-update-business").click(function(e){
        e.preventDefault();
//        load_business_update($("#business-id-" + $(this).attr("count")).val());
        load_business_update($(this));
    });
    // index old business
    $("#div-old-business").find(".business-div").each(function(index) {
        index_business_div($(this), false);
    });

    // index new business
    $("#div-new-business").find(".business-div").each(function(index) {
        index_business_div($(this), true);
    });

    // index decisions
    $("#div-decisions").find(".decision-div").each(function(index) {
        index_decision_div($(this), true);
    });

    // add listener to the new business button
    $("#btn-new-business").click(function(e){
        e.preventDefault();
        load_business_form();
    });

    // add listener to the new decision button
    $("#btn-new-decision").click(function(e){
        e.preventDefault();
        load_decision_form();
    });
    // update minutes on change of inputs
    let arr = ['id_meeting_date', 'id_start_time', 'id_attending', 'id_minutes_text', 'id_memberships', 'id_balance',
               'id_discussion', 'id_end_time'];
    arr.forEach(function(item) {
        $("#" + item).change(function(e){
            update_minutes($(this))
        });
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
    return pad(dt.getHours(), 2) + ":" + pad(dt.getMinutes(), 2) + ":" + pad(dt.getSeconds(), 2);
}

function index_business_div(container, new_business) {
    container.attr("new-business", new_business)
    if(container.find('[name="resolved_bool"]').prop('checked')) {
        container.find("[name=business]").prop('disabled', true);
    }
    console.log(new_business)

    if (new_business) {
        container.find(".btn-update-business").hide();
    }
    else {
        container.find("[name=business]").prop('disabled', true);
    }

    container.find("[name=business]").change(function(e){
        save_business(container);
    });

    $(".resolved-check").change(function(e){
        save_business($(this).parents(".business-div"));
    });

    $("btn-update-business").click(function(e){
        e.preventDefault();
        load_business_update($(this));
    });
}

function index_decision_div(container) {

    container.find("[name='decision_date']").hide()
    console.log(container.find("[name='decision_date']").val())
//    $("#decision_decision_date-" + report_count).hide()
    container.find("[name='text']").change(function(e){
        e.preventDefault();
        save_decision(container);
    });

}

function index_report_div(container) {
    container.find("[name='report']").change(function(e){
        e.preventDefault();
        save_report(container);
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
    await $.get(url_business, { report_index: report_count }, function(data, status){
        $("#div-new-business").append(data);
        $("#business_minutes_" + report_count).val(minutes_id);
        index_business_div($("#business-div-" + report_count), true)
        report_count = report_count + 1;
    });
}

async function load_business_update(btn) {
    let business_div = btn.parents(".business-div")
    await $.get(url_business_update, { report_index: report_count }, function(data, status){
        business_div.find(".div-business-update").append(data);
        $("#update_business_" + report_count ).val(business_div.find("[name='business_id']").val());
        $("#update_update_text_" + report_count).change(function(e){
            save_update($(this));
        });
        report_count = report_count + 1;
    });
}

async function load_decision_form() {
    await $.get(url_decision, { report_index: report_count }, function(data, status){
        $("#div-decisions").append(data);
        index_decision_div($("#decision-div-" + report_count))
    });
}

async function load_report_form(container, owner) {
    await $.get(url_report, { report_index: report_count }, function(data, status){
        console.log(status)
        container.append(data);
        container.find('[name="owner"]').val(owner);
        console.log(container.find('[name="owner"]').val());
        container.find('[name="minutes"]').val(minutes_id);
        index_report_div($("#report-div-" + report_count))
        report_count = report_count + 1;
    });
}

async function save_business(business_div) {

    let url_string = url_business
    console.log(business_div.attr("id"))
    if (business_div.find('[name="business_id"]').val() != "") {
        url_string = url_string + "/" + business_div.find('[name="business_id"]').val()
    }

    await $.post(url_string, {
        csrfmiddlewaretoken: business_div.find('[name="csrfmiddlewaretoken"]').val(),
        added_date: business_div.find('[name="added_date"]').val(),
        minutes: business_div.find('[name="business_minutes"]').val(),
        business: business_div.find('[name="business"]').val(),
        resolved_bool: business_div.find('[name="resolved_bool"]').prop('checked'),
    }, function(data, status){
        business_div.find('[name="business_id"]').val(data.business_id);
        indicate_saved(data.success)

        business_div.find('[name="resolved_bool"]').prop('disabled', false);
    }, "json");
}

async function save_decision(container) {
    let url_string = url_decision
    if (container.find("[name='decision_id']").val() != "") {
        url_string = url_string + "/" + container.find("[name='decision_id']").val();
    }
    await $.post(url_string, {
        csrfmiddlewaretoken: container.find('[name="csrfmiddlewaretoken"]').val(),
        decision_date: container.find("[name='decision_date']").val(),
        text: container.find("[name='text']").val()
    }, function(data, status){
        container.find("[name='decision_id']").val(data.decision_id);
        indicate_saved(data.success);
    }, "json");
}

async function save_report(report_container) {

    let url_string = url_report
    console.log(report_container.find('[name="report_id"]').val())
    if (report_container.find('[name="report_id"]').val() != "") {
        url_string = url_string + "/" + report_container.find('[name="report_id"]').val();
    }
    let report_data = report_container.find('[name="report"]').val();
    await $.post(url_string, {
        csrfmiddlewaretoken: report_container.find('[name="csrfmiddlewaretoken"]').val(),
        owner: report_container.find('[name="owner"]').val(),
        minutes: report_container.find('[name="minutes"]').val(),
        report: report_data
    }, function(data, status){
        console.log(report_data)
        report_container.find('[name="report_id"]').val(data.report_id);
        indicate_saved(data.success);
//        report_element.val(report_data);
    }, "json");
}

async function save_update(update_element) {
    let update_row = update_element.parents(".div-update-row")
//    let count = update_element.attr('count')
    let url_string = url_business_update
    if (update_row.find("[name='update_id']").val() != "") {
        url_string = url_string + "/" + update_row.find("[name='update_id']").val()
    }
    await $.post(url_string, {
        csrfmiddlewaretoken: update_row.find('[name="csrfmiddlewaretoken"]').val(),
        business: update_row.find('[name="business"]').val(),
        update_text: update_element.val()
    }, function(data, status){
        update_row.find('[name="business"]').val(data.update_id);
        indicate_saved(data.success);
    }, "json");
}

async function update_minutes() {
    if (minutes_id != null){
        let post_data = {
            'csrfmiddlewaretoken': $('#minutes-form').find('[name="csrfmiddlewaretoken"]').val(),
            'update': true
        }
        let arr = ['meeting_date', 'start_time', 'attending', 'minutes_text', 'memberships', 'balance',
                   'discussion', 'end_time'];
        arr.forEach(function(item) {
            post_data[item] = $("#id_" + item).val();
        });

        await $.post(url_minutes, post_data, function(data, status){
            if (status == 'success') {
                $("#div-saved-message").html("Saved at:" + get_time());
            }

        }, "json");
    }
}