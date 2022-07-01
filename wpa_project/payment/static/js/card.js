"use strict";

async function initializeCard(payments) {
 const card = await payments.card();
 await card.attach('#card-container');
 return card;
}

document.addEventListener('DOMContentLoaded', async function () {
    $("#id_source_id").hide()
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

    async function handlePaymentMethodSubmission(event, paymentMethod) {
       event.preventDefault();
       console.log('handle payment');

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
        await handlePaymentMethodSubmission(event, card);
//        $("#id_source_id").show()
        $("#payment-form").submit();
    });

});


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