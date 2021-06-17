"use strict";
$.ajaxSetup({traditional: true});
var started_status = false;
$(document).ready(function(){
    $(".student-check").each(show_new_student);
    get_reg_table();
    $("#id_beginner_class").click(get_class_status);
});

async function get_class_status() {
    // get the class status from the server. tells us how many openings there are in the class.
    let d = $("#id_beginner_class").val();
    if(d != "") {
        let data = await $.get("class_status/" + $("#id_beginner_class").val() +"/", function(data, status){
            let msg = "Class openings:</br> &nbsp;&nbsp; New Students: " +  data['beginner'] + " Returning: " + data['returnee'];
            $("#class-availible").html(msg);
        });
    }
}

async function get_reg_table() {
    // get the classes that this 'family' is registered for.
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

    $(".pay_status").each(pay_status_links);
    if (started_status){
        alert("You have an incomplete payment and are not registered for the class.\n" +
        "If you wish to process the payment click on the 'Started' link. " +
        "If can't attend please unregister by selecting the class(es) you wish to cancel and click the Unregister button')");
    }
}

function pay_status_links(i, el) {
    let e = $(el)
    if (e.html().trim() == 'start') {
        started_status = true;
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
    // to unregister student(s) from a class.
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

        //       Send the unregister request to the server
        let data = await $.post("unregister_class", {
            "class_list": unreg_list,
            csrfmiddlewaretoken: $('[name="csrfmiddlewaretoken"]').val()
        }, function(data, status){
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

function show_new_student(i, el) {
    // puts "New Student" next to a student's name if they have not been though the safety class.
    let e = $(el)
    if (e.attr("is_beginner") == "T") {
        $("#is-new-student-" + i).html("New Student")
    }
    else{
        $("#is-new-student-" + i).html("Returning Student")
    }

}