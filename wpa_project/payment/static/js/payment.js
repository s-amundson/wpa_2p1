"use strict";

async function initializeCard(payments) {
 const card = await payments.card();
 await card.attach('#card-container');
 return card;
}

$(document).ready(async function(){
//    var cost_no_donation = parseFloat($("#id_amount").val());
    $("#id_amount").prop("disabled", true);
    $("#id_donation").change(function () {
        if ($("#id_donation").val() < 0 ){
            $("#id_donation").val(0)
        }
        $("#id_amount").val(cost_no_donation + parseFloat($("#id_donation").val()))
    });
    $("#id_card").change(function () {
        eval_saved_card();
    });
    eval_saved_card();
    $("#card-remove-button").click(function() {
        $("#payment-form").attr('action', url_remove_card);
        $("#payment-form").submit();
    });
    if (!user_auth) {
        $("#id_card").hide();
        $("#id_save_card").parent().hide();
    }
});

document.addEventListener('DOMContentLoaded', async function () {
    if (!window.Square) {
      throw new Error('Square.js failed to load properly');
    }
    const payments = window.Square.payments(window.applicationId, window.locationId);
    let card;
    try {
      card = await initializeCard(payments);
    } catch (e) {
      console.error('Initializing Card failed', e);
      return;
    }
    console.log('initialized');
    eval_saved_card();
    async function handlePaymentMethodSubmission(event, paymentMethod) {
       event.preventDefault();
       console.log('handle payment');
       if ($("#id_card").val() != "0") {
         return;
       }
       try {
         // disable the submit button as we await tokenization and make a
         // payment request.
         cardButton.disabled = true;
         const token = await tokenize(paymentMethod);
         console.log(token)
         $("#id_source_id").val(token);
         console.log('token made');
         $("#card-button").prop("disabled", false);

       } catch (e) {
         cardButton.disabled = false;
         displayPaymentResults('FAILURE');
         console.error(e.message);
       }
    }

    const cardButton = document.getElementById(
        'card-button'
    );
    cardButton.addEventListener('click', async function (event) {
        console.log('card button clicked');
        if(cost_no_donation + parseFloat($("#id_donation").val()) > 0) {
            console.log('pay');
            await handlePaymentMethodSubmission(event, card);
            $("#id_amount").prop("disabled", false);
        }
        else {
//            await createPayment('no-payment')
            $("#id_source_id").val('no-payment');
        }
        $("#id_amount").prop("disabled", false);
        $("#payment-form").submit();
    });
//    $("#payment-form").submit(function(e){
//        e.preventDefault();
//        createPayment('no-payment')
//    });
});

function eval_saved_card() {
    console.log($("#id_card").val())
    if ($("#id_card").val() == "0") {
        console.log("new card");
        $("#id_save_card").prop("disabled", false);
//        $("#card-button").prop("disabled", true);
        $("#card-container").show();
        $("#card-remove-button").hide();
    }
    else {
        $("#id_save_card").prop("disabled", true);
        $("#card-button").prop("disabled", false);
        $("#card-container").hide();
        $("#card-remove-button").show();
    }
}

// This function tokenizes a payment method.
// The ‘error’ thrown from this async function denotes a failed tokenization,
// which is due to buyer error (such as an expired card). It is up to the
// developer to handle the error and provide the buyer the chance to fix
// their mistakes.
async function tokenize(paymentMethod) {
    const tokenResult = await paymentMethod.tokenize();
    if (tokenResult.status === 'OK') {
        return tokenResult.token;
    } else {
        let errorMessage = `Tokenization failed-status: ${tokenResult.status}`;
    if (tokenResult.errors) {
        errorMessage += ` and errors: ${JSON.stringify(
            tokenResult.errors
        )}`;
    }
        throw new Error(errorMessage);
    }
}