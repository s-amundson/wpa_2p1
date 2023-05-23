"use strict";
$(document).ready(function(){
    $("#btn-announcement-preview").click(function(){
        console.log('preview')
        $("#announcement-container").html($("#id_announcement").val())
    });
});