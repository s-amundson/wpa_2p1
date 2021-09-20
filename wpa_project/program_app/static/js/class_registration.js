"use strict";
$.ajaxSetup({traditional: true});
var started_status = false;
$(document).ready(function(){
    $(".student-check").each(show_new_student);
    get_reg_table();
    $("#id_beginner_class").click(get_class_status);

    get_calendar();
    $("#beginner-class-form").hide()
    $("#calendar-show-btn").hide()
    $("#calendar-prev-btn").hide()
    $("#calendar-show-btn").click(function (){
        $("#div-calendar").show()
    });

    $("#calendar-prev-btn").click(function () {
        month = month - 1;
        get_calendar();
    });

    $("#calendar-next-btn").click(function () {
        month = month + 1;
        get_calendar();
    });

});

function check_dob(i, el) {
//    if ($("#id_beginner_class").val() != "") {
//        let e = $(el);
//        console.log($("#id_beginner_class").val())
//        let dob = new Date(e.attr('dob'));;
//        console.log(dob)
//        let class_date = new Date($("#id_beginner_class").val());
//        let of_age = new Date(class_date.setFullYear(class_date.getFullYear() - 9));
//        console.log(of_age);
//        console.log(dob < of_age)
//        if (dob < of_age) {
//            e.attr("disabled", false);
//        }
//        else {
//            e.attr("disabled", true);
//            e.attr("checked", false);
//            if ($("#is-new-student-" + i).html() == "New Student") {
//                $("#is-new-student-" + i).html("New Student, Students must be 9 years or older to attend")
//            }
//            else if ($("#is-new-student-" + i).html() == "Returning Student") {
//                $("#is-new-student-" + i).html("Returning Student, Students must be 9 years or older to attend")
//            }
//        }
//    }
}

async function get_calendar() {
    await $.get("class_calendar/" + month, function(data, status){
        $("#div-calendar").html(data);
        console.log(status);
        $(".bc-btn").click(select_class)
        let d = new Date().getMonth() + 1 // Jan is 0 in javascript
        console.log(d)
        if (month == d) {
            $("#calendar-prev-btn").hide();
        }
        else {
            $("#calendar-prev-btn").show()
        }
    });

}

async function get_class_status() {
    // get the class status from the server. tells us how many openings there are in the class.
    let d = $("#id_beginner_class").val();
    if(d != "") {
        let data = await $.get("class_status/" + $("#id_beginner_class").val() +"/", function(data, status){
            let msg = "Class openings:</br> &nbsp;&nbsp; ";
            msg += "New Students: " +  data['beginner'] + ", starting at " + data['beginner_time'];
            msg += "</br> &nbsp;&nbsp; Returning: " + data['returnee'] + ", starting at " + data['returnee_time'];
            $("#class-availible").html(msg);
        });
    }
    $(".student-check").each(check_dob);
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
    if ($(".pay_status").length == 0) {
        $("#registered_classes").hide()
    }
    else {
        $(".pay_status").each(pay_status_links);
        if (started_status){
            alert("You have an incomplete payment and are not registered for the class.\n" +
            "If you wish to process the payment click on the 'Started' link. " +
            "If can't attend please unregister by selecting the class(es) you wish to cancel and click the Unregister button')");
        }
        $("#registered_classes").show()
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
    if(unreg_list.length == 0){
        alert("Please select a class to unregister")
        }
    if(unreg_list.length == 1){
        if ($("#donation").prop('checked') == true) {
            getConfirm = confirm("Please confirm that you wish to unregister for this class.\n You will be donating " +
            refund + " to the club");
            }
        else {
            getConfirm = confirm("Please confirm that you wish to unregister for this class.\n You will be refunded " +
            refund + " to your card in 5 to 10 business days");
            }

        }
    else if (unreg_list.length > 1) {
        if ($("#donation").prop('checked') == true) {
            getConfirm = confirm("Please confirm that you wish to unregister for these classes.\n You will be donating " +
            refund + " to the club");
            }
        else {
            getConfirm = confirm("Please confirm that you wish to unregister for these classes.\n You will be refunded " +
            refund + " to your card(s) in 5 to 10 business days");
            }
        }
    if (getConfirm) {

        //       Send the unregister request to the server
        let data = await $.post("unregister_class", {
            "class_list": unreg_list,
            csrfmiddlewaretoken: $('[name="csrfmiddlewaretoken"]').val(),
            'donation': $("#donation").prop('checked')
        }, function(data, status){
            return data;
            }, "json");

        //      request new table from server
        console.log('get table from server')
        get_reg_table();
        alert("You have successfully been unregistered from the class.\n")
    }
    else {
        console.log('canceled');
    }
}

function select_class() {
    $("#div-calendar").hide()
    console.log($(this).attr('bc_id'))
    $("#id_beginner_class").val($(this).attr('bc_id'))
    $("#beginner-class-form").show()
    $("#calendar-show-btn").show()
    $("#calendar-next-btn").hide()
    $("#calendar-prev-btn").hide()
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