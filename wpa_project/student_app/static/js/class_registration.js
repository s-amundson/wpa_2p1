"use strict";
$(document).ready(function(){
    $.get("class_registered_table", function(data, status){
        $("#registered_table").html(data);
    });

});