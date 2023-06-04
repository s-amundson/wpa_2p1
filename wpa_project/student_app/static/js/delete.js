"use strict";
$(document).ready(function() {
    $("#remove-student").hide();
    update_delete();
    $("#id_removal_choice").change(function() {
        console.log($(this).val());
        update_delete();
    });
});

function update_delete() {
    if($("#id_removal_choice").val() == "remove") {
        $("#remove-student").show();
        $("#delete-student").hide();
        $("label[for=id_delete]").html('Enter "remove" in order to remove this student');
        $("button[name=button]").html('Remove Student');
    }
    else {
        $("#remove-student").hide();
        $("#delete-student").show();
        $("label[for=id_delete]").html('Enter "delete" in order to remove this student');
        $("button[name=button]").html('Delete Student');
    }
}