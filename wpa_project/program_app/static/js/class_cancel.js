"use strict";
$.ajaxSetup({traditional: true});

$(document).ready(function(){
    get_reg_table();
});

async function get_reg_table() {
    // get the classes that this 'family' is registered for.
    let data = await $.get(url_class_registered_table, function(data, status){
        $("#registered_table").html(data);

        $("#cancel_form").submit(function(e){
            e.preventDefault();
            post_cancel()
        });
    });

}

async function post_cancel() {
    // to cancel a student(s) registration for a class.
    let refund = 0;
    let cancel_list = [];
    let getConfirm = false;
//    let class_id = "";
    $(".cancel-check").each(function(i, obj) {
        if($(this).prop('checked') == true) {
            cancel_list.push(1);
            refund += parseInt($(this).parent().find(".cancel-amount").val());
        }
    });
    if(cancel_list.length == 0){
        alert_notice("Notice", "Please select a class to cancel.")
    }
    if ('confirm' in window) {
        if(cancel_list.length == 1){
            if (refund == 0) {
                getConfirm = confirm("Please confirm that you wish to cancel your registration for this class.");
                }
            else if ($("#id_donate").prop('checked') == true) {
                getConfirm = confirm("Please confirm that you wish to cancel your registration for this class.\n You will be donating " +
                refund + " to the club");
                }
            else {
                getConfirm = confirm("Please confirm that you wish to cancel your registration for this class.\n You will be refunded $" +
                refund + " to your card in 5 to 10 business days");
                }
            }
        else if (cancel_list.length > 1) {
            if (refund == 0) {
                    getConfirm = confirm("Please confirm that you wish to cancel your registration for these classes.");
                }
            else if ($("#id_donation").prop('checked') == true) {
                getConfirm = confirm("Please confirm that you wish to cancel your registration for these classes.\n You will be donating " +
                refund + " to the club");
                }
            else {
                getConfirm = confirm("Please confirm that you wish to cancel your registration for these classes.\n You will be refunded $" +
                refund + " to your card(s) in 5 to 10 business days");
                }
            }
        console.log(getConfirm)
    }
    else {
        getConfirm = true;
    }
    if (getConfirm) {
        let data = await $.post(url_class_registered_table, $("#cancel_form").serializeArray(), function(data, status){
            $("#registered_table").html(data);

            $("#cancel_form").submit(function(e){
                e.preventDefault();
                post_cancel()
            });
        });
    }
    else {
        console.log('canceled');
    }
}
