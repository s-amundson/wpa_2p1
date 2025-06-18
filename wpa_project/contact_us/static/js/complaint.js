"use strict";
$(document).ready(function(){
    $("#id_category").change(function(e){
        if ($(this).val() == "harassment") {
            $("#id_anonymous").prop("disabled", false);
        } else {
            $("#id_anonymous").prop('checked', false);
            $("#id_anonymous").prop("disabled", true);
        }
    });
    $("#id_anonymous").prop("disabled", true);
});