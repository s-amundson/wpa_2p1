"use strict";
$(document).ready(function(){
    $(".not_empty").blur(function() {
        return set_valid($(this), $(this).val() != '')
    });
    $(".email").blur(function () {
        var mail_format = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/
        console.log(mail_format.test($(this).val()))
        return set_valid($(this), mail_format.test($(this).val()))
    });
    $(".numeric").blur(function () {
        var numbers = /^[0-9]+$/;
        set_valid($(this), numbers.test($(this).val()))
    });
    $("#id_wpa_membership_number").blur(function() {
        if ($(this).val() != ''){
            var numbers = /^[0-9]+$/;
            set_valid($(this), numbers.test($(this).val()))
        } else {
            set_valid($(this), true)
        }
    })
    $(".date_input").datepicker(
        {
          format:'yyyy-mm-dd',
        })
//    $(function () {
//            $(".date_input").datepicker(
//            {
//              format:'yyyy-mm-dd',
//            })
//        })
})

function reg_check (input) {
    var i = document.getElementById(input)
    if (i.value == '') {
        i.style = 'border: 3px solid Tomato;';
        return false;
    } else {
        i.style = 'border: 3px solid Green;';
        return true;
    }
}

function select_check (in_select) {
    console.log('select_check' + in_select.value)
    if (in_select.value === 'invalid') {
        in_select.style = 'border: 3px solid Tomato;'
        return false
    } else {
        in_select.style = 'border: 3px solid Green;'
        return true
    }
}
function set_valid (input, valid) {
    if (valid) {
        $(input).attr("style", 'border: 3px solid Green;');
        return true;
    } else {
        $(input).attr("style", 'border: 3px solid Tomato;');
        return false;
    }
}

