"use strict";
$.ajaxSetup({traditional: true});
var started_status = false;
$(document).ready(function(){
    $(".student-check").each(show_new_student);
    get_reg_table();
    $("#id_beginner_class").click(get_class_status);
    get_class_status();

    $("#myModal").modal("show");
});

async function get_calendar() {
    await $.get(url_calendar + month, function(data, status){
        $("#div-calendar").html(data);
        $(".bc-btn").click(select_class)
        let d = new Date().getMonth() + 1 // Jan is 0 in javascript
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
    console.log(d)
    let msg = ""

    if(d == "" | d == 'null') {
        $("#class-description").html("")
    }
    else {
        let data = await $.get(url_class_status + $("#id_beginner_class").val() +"/", function(data, status){
            msg = "Class openings:</br> &nbsp;&nbsp; ";
            msg += "New Students: " +  data['beginner'];
            msg += "</br> &nbsp;&nbsp; Returning: " + data['returnee'];
            if($("#is_instructor").val() == "True") {
                msg += "</br> &nbsp;&nbsp; Instructors: " + data['instructor'];
            }
            else {
                $("#class-description").html("")
                if(data["class_type"] == "beginner") {
                    $(".student-check").each(function(e) {
                        console.log($(this).attr("is_beginner") != "T")
                        if ($(this).attr("is_beginner") != "T") {
                            $(this).attr('checked', false);
                        }
                    });
                    $("#class-description").html("This class is reserved for new students. Student's may only register for one upcoming beginner class.")
                }
                if(data["class_type"] == "returnee") {
                    $(".student-check").each(function(e) {
                        if ($(this).attr("is_beginner") == "T") {
                            $(this).attr('checked', false);
                        }
                    });
                    $("#class-description").html("This class is reserved for students that have been to at least one of our classes before.")
                }
                $("#class-description").append('</br> Please show up 15 minutes prior to class time.')
            }

        });
    }
    $("#class-available").html(msg);
}

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
    let unreg_list = [];
    let getConfirm = false;
    let class_id = "";
    $(".unreg").each(function(i, obj) {
        class_id = $(this).attr("class_id");
        console.log($(this).parents("tr").find(".pay_status").find("a").length)
        if($(this).prop('checked') == true) {
            if($(this).parents("tr").find(".pay_status").find("a").length) {
                incomplete = incomplete + 1;
                console.log(incomplete)
            }
            refund += parseInt($(this).parent().find(".unreg_cost").val());
            unreg_list.push(class_id);
        }
    });
    if(unreg_list.length == 0){
        alert_notice("Notice", "Please select a class to unregister")
    }
    if ('confirm' in window) {
        if(unreg_list.length == 1){
            if (unreg_list.length == incomplete) {
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
            if (unreg_list.length == incomplete) {
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

function select_class() {
    $("#div-calendar").hide();
    $("#id_beginner_class").val($(this).attr('bc_id'));
    $("#beginner-class-form").show();
    $("#calendar-show-btn").show();
    $("#calendar-next-btn").hide();
    $("#calendar-prev-btn").hide();
    get_class_status();
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