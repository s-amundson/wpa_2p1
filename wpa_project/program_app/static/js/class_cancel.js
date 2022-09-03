"use strict";
$.ajaxSetup({traditional: true});

$(document).ready(function(){
    if (family) {
    get_reg_table();
    }
});

async function get_reg_table() {
    // get the classes that this 'family' is registered for.
    let data = await $.get(url_class_registered_table, function(data, status){
        $("#registered_table").html(data);

        $("#unreg_form").submit(function(e){
            e.preventDefault();
            post_unregister()
        });
    });

}

async function post_unregister() {
    // to unregister student(s) from a class.
    let refund = 0;
    let incomplete = 0;
    let waiting = 0
    let unreg_list = [];
    let getConfirm = false;
    let class_id = "";
    $(".unreg").each(function(i, obj) {
        class_id = $(this).attr("class_id");
        console.log($(this).parents("tr").find(".pay_status").find("a").length)
        if($(this).prop('checked') == true) {
            if($(this).prop("class").search("start")) {
                incomplete = incomplete + 1;
                console.log(incomplete)
            }
            else if($(this).prop("class").search("waiting")) {
                waiting = waiting + 1;
            }
            else {
                refund += parseInt($(this).parent().find(".unreg_cost").val());
            }
            unreg_list.push(class_id);
        }
    });
    if(unreg_list.length == 0){
        alert_notice("Notice", "Please select a class to unregister")
    }
    if ('confirm' in window) {
        if(unreg_list.length == 1){
            if (unreg_list.length == incomplete | unreg_list.length == waiting) {
                getConfirm = confirm("Please confirm that you wish to unregister for this class.");
                }
            else if ($("#id_donation").prop('checked') == true) {
                getConfirm = confirm("Please confirm that you wish to unregister for this class.\n You will be donating " +
                refund + " to the club");
                }
            else {
                getConfirm = confirm("Please confirm that you wish to unregister for this class.\n You will be refunded " +
                refund + " to your card in 5 to 10 business days");
                }
            }
        else if (unreg_list.length > 1) {
            if (unreg_list.length == incomplete | unreg_list.length == waiting) {
                    getConfirm = confirm("Please confirm that you wish to unregister for this class.");
                }
            else if ($("#id_donation").prop('checked') == true) {
                getConfirm = confirm("Please confirm that you wish to unregister for these classes.\n You will be donating " +
                refund + " to the club");
                }
            else {
                getConfirm = confirm("Please confirm that you wish to unregister for these classes.\n You will be refunded " +
                refund + " to your card(s) in 5 to 10 business days");
                }
            }
        console.log(getConfirm)
    }
    else {
        getConfirm = true;
    }
    if (getConfirm) {
        $("#unreg_form").unbind();
        $("#unreg_form").submit();

    }
    else {
        console.log('canceled');
    }
}
