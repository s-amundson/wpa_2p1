
$(document).ready(function() {
    console.log('page loaded');
    load_student_table();

    $("#btn-add-student").click(function(){
        load_student_form();
    });

    $("#btn-address-edit").click(function(){
        console.log($(this).attr("family_id"))
        load_student_family_form($(this).attr("family_id"));
    });

//    $("#add-student").modalForm({
//        formURL: "{% url 'add_student' %}"
//    });
});

async function add_student_function(student_id) {
    console.log('on submit')
    var url_string = "student_api"
    if(student_id) {
        url_string = "student_api/" + student_id + "/";
        $("#student-row-" + student_id).show();
    }
    console.log(url_string);
    let data = await $.post(url_string, {
            csrfmiddlewaretoken: $('[name="csrfmiddlewaretoken"]').val(),
            'first_name': $("#id_first_name").val(),
            'last_name' : $("#id_last_name").val(),
            'dob': $("#id_dob").val()
        }, function(data, status){
            console.log(data)
            return data;
            }, "json");
    $("#student_add_div").hide();
    $("#btn-add-student").show();
    load_student_table();
}

function load_student_family_form(family_id) {
    console.log(family_id)
    $("#student-family-address").hide();

    let url_string = "student_register/" + family_id + "/";
    console.log(url_string);
    $.get(url_string, function(data, status){
        $("#student-family-form").html(data);
        $("#student-family-form").show();

        $("#family-form").submit(function(e){
            e.preventDefault();
            post_family_function(family_id)
        });

    });
}

function load_student_form(student_id) {
    console.log(student_id)
    $("#student_add_div").show();
    $("#btn-add-student").hide()
    var url_string = "add_student"
    if(student_id) {
        url_string = "add_student/" + student_id + "/"
        $("#student-row-" + student_id).hide()
    }
    console.log('load form')
    console.log(url_string)
    $.get(url_string, function(data, status){
        $("#student_add_div").html(data);
        if(student_id) {
            $("#btn-student-form").html("Update")
        }
        else {
            $("#btn-student-form").html("Add")
        }
        $("#student_form").submit(function(e){
            e.preventDefault();
            add_student_function(student_id)
        });
    });
}

function load_student_table() {
    $.get("student_table", function(data, status){
        $("#student-table-div").html(data);

        if($(".student_row").length == 0) {
            //  no students therefore we need to load the student form
            load_add_student_form();
        }
        else {
            $("[id^=btn-edit]").click(function(){
                load_student_form($(this).attr("student-id"));
            });
        }
    });
}

async function post_family_function(family_id) {
    console.log('on submit')
    let url_string = "student_family_api/" + family_id + "/";
    let data = await $.post(url_string, {
        csrfmiddlewaretoken: $('[name="csrfmiddlewaretoken"]').val(),
        'street': $("#id_street").val(),
        'city' : $("#id_city").val(),
        'state': $("#id_state").val(),
        'post_code': $("#id_post_code").val(),
        'phone': $("#id_phone").val()
    }, function(data, status){
        console.log(data)
        return data;
    }, "json");
    $("#address1").html($("#id_street").val());
    $("#address2").html($("#id_city").val() + " " + $("#id_state").val() + " " + $("#id_post_code").val())
    $("#phone").html($("#id_phone").val())

    $("#student-family-form").html("");
    $("#student-family-form").hide();
    $("#student-family-address").show();
}
