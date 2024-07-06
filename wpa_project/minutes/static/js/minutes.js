"use strict";

$(document).ready(async function() {
    await old_business_urls.forEach(async function(url) {
        await $.get(url, function(data, status){
            if (status == 'success') {
//                console.log(data);
                $("#old-business-forms").html($("#old-business-forms").html() + data);
                $(".business-form :input").off('change');
                $(".business-form :input").change(function(e){
                    save_business($(this));
                });
            }
        });
        console.log(url);
    });
    if (new_business_urls.length > 0) {
        await new_business_urls.forEach(async function(url) {
            await $.get(url, function(data, status){
                if (status == 'success') {
    //                console.log(data);
                    $("#new-business-forms").html($("#new-business-forms").html() + data);
                    $(".business-form :input").off('change');
                    $(".business-form :input").change(function(e){
                        save_business($(this));
                    });
                }
            });
        });
    } else {
        await $.get(new_business_url, function(data, status){
            if (status == 'success') {
                $("#new-business-forms").html($("#new-business-forms").html() + data);
                $(".business-form :input").off('change');
                $(".business-form :input").change(function(e){
                    save_business($(this));
                });
            }
        });
    }


    $(".btn-report").click(function(e) {
        e.preventDefault();
        let empty_form = $(this).parent().find(".empty_form")
        let total_forms = $(this).parent().find("[name$='TOTAL_FORMS']")
        let html = empty_form.html().replace(/__prefix__/g, total_forms.val());
        console.log(html)
        total_forms.val(parseInt(total_forms.val()) + 1)
        $(html).insertBefore(empty_form);
        let new_form = empty_form.prev();
        let prior_form = new_form.prev();
        new_form.find(":input").each(function() {
            let el_id = $(this).attr('id').split('-')[$(this).attr('id').split('-').length -1];
            if (['report', 'id'].indexOf(el_id) === -1) {
                $(this).val(prior_form.find("[name$='" + el_id + "']").val());
            }
        });
        new_form.find(".minutes-input").change(function(e){
            console.log($(this));
            update_minutes()
        });
    });

    $(".minutes-input").not(".report").change(function(e){
        console.log($(this));
        update_minutes()
    });
    $(".report").change(save_report);

    if (minutes_edit == false) {
        console.log('lock editing')
        $(":input").prop('disabled', true);
    }
    $("#btn-end").click(function(e){
        e.preventDefault();
        $("#id_end_time").val(get_time)
        $("#minutes-form").submit();
    });

    console.log('done loading')

});

function get_time() {
    var dt = new Date();
    return pad(dt.getFullYear(), 4) + '-' + pad(dt.getMonth() + 1, 2) + "-" + pad(dt.getDate(), 2) + " " + pad(dt.getHours(), 2) + ":" + pad(dt.getMinutes(), 2) + ":" + pad(dt.getSeconds(), 2);
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

async function save_business(element) {
    console.log('form changed');
    console.log(element.closest('form').serializeArray());
//    $(this).closest('form').submit();
    await $.post(element.closest('form').attr('action'), element.closest('form').serializeArray(), function(data, status){
        if (status == 'success') {
            $("#div-saved-message").html("Saved at:" + get_time());
            element.closest('form').replaceWith(data)
            $(".business-form :input").change(function(e){
                    save_business($(this));
                });
        } else {
            console.log('failed save');
        }
    });
}

async function save_report() {
    console.log('report change');
    let url_string = url_report
    let element_id = $(this).parent().find("[name$='id']")
    if ($(this).parent().find("[name$='id']").val() != "") {
        url_string = url_string + $(this).parent().find("[name$='id']").val() + "/";
    }

    await $.post(url_string, {
        csrfmiddlewaretoken: $("#minutes-form").find('[name="csrfmiddlewaretoken"]').val(),
        owner: $(this).parent().find("[name$='owner']").val(),
        minutes: $(this).parent().find("[name$='minutes']").val(),
        report: $(this).parent().find("[name$='report']").val(),
        id: $(this).parent().find("[name$='id']").val()
    }, function(data, status){
        console.log(data.report_id);
        element_id.val(data.report_id);
        indicate_saved(data.success);
    }, "json");
}

async function update_minutes() {
    if (minutes_id != null){
        console.log('update minutes')
        await $.post(url_minutes, $("#minutes-form").serializeArray(), function(data, status){
            if (status == 'success') {
                $("#div-saved-message").html("Saved at:" + get_time());
                console.log("Saved at:" + get_time())
            }
        }, "json");
    }
}