"use strict";

$(document).ready(function(){
    $("#id_session").change(function(e){
        e.preventDefault();
        load_class_table();
    });

});


function load_class_table(){
    if ($("#id_session").val() == "") {
        return;
    }
    $.get(class_list_url + $("#id_session").val(), function(data, status){
        $("#class-table-div").html(data);
    });
}

