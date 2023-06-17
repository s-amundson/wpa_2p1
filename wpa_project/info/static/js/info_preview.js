"use strict";
$(document).ready(function(){
    $("#btn-info-preview").click(function(){
        console.log('preview');
        if($("#id_announcement").length) {
            console.log('anouncement');
            $("#info-preview-container").html($("#id_announcement").val());
        }
        else if($("#id_bio").length) {
            console.log('bio')
            $("#info-preview-container").html($("#id_bio").val());
        }
    });
});