"use strict";
$.ajaxSetup({traditional: true});
$(document).ready(function(){
    get_reg_table();
});

async function get_reg_table() {
    let data = await $.get("class_registered_table", function(data, status){
        $("#registered_table").html(data);
        if($(".unreg").length > 0) {
            $("#unreg_form").show();
        }
        else{
            $("#unreg_form").hide();
        }
        $("#unreg_form").submit(function(e){
            e.preventDefault();
            post_unregister()
        });
    });

    $(".pay_status").each(pay_status_links)
//    function(e){
//        pay_status_links($(this))
//    });
}
function pay_status_links(i, el) {
    let e = $(el)
    console.log(e.html().trim())

    if (e.html().trim() == 'start') {
        console.log('here')
        var a = document.createElement('a');

        // Create the text node for anchor element.
        var link = document.createTextNode("Started");

        // Append the text node to anchor element.
        a.appendChild(link);

        // Set the title.
        a.title = "Started";

        // Set the href property.
        a.href = e.attr("curl");

        e.html(a);
    }
}
async function post_unregister() {
    console.log('on submit')
    let refund = 0;
    let unreg_list = [];
    let getConfirm = false;
    let class_id = "";
    $(".unreg").each(function(i, obj) {
        class_id = $(this).attr("class_id");
        console.log("class_id " + class_id);
        if($(this).prop('checked') == true) {
            refund += parseInt($("#cost_" + class_id).val());
            unreg_list.push(class_id);
        }
        console.log(refund);
    });
    if(unreg_list.length == 1){
        getConfirm = confirm("Please confirm that you wish to unregister for this class.\n You will be refunded " +
        refund + " to your card");
        }
    else if (unreg_list.length > 1) {
        getConfirm = confirm("Please confirm that you wish to unregister for these classes.\n You will be refunded " +
        refund + " to your card(s)");
        }
    if (getConfirm) {
        console.log("submit");
        console.log(unreg_list);

        //       Send the unregister request to the server
        let data = await $.post("unregister_class", {
            "class_list": unreg_list,
            csrfmiddlewaretoken: $('[name="csrfmiddlewaretoken"]').val()
        }, function(data, status){
            console.log(data)
            return data;
            }, "json");

        //      request new table from server
        console.log('get table from server')
        get_reg_table();
    }
    else {
        console.log('canceled');
    }
}
