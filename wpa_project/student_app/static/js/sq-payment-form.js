
async function initializeCard(payments) {
 const card = await payments.card();
 await card.attach('#card-container');
 return card;
}

document.addEventListener('DOMContentLoaded', async function () {
    $("#receipt").hide();
    $("#index-link").hide();
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

    async function handlePaymentMethodSubmission(event, paymentMethod) {
       event.preventDefault();

       try {
         // disable the submit button as we await tokenization and make a
         // payment request.
         cardButton.disabled = true;
         const token = await tokenize(paymentMethod);
         const paymentResults = await createPayment(token);
         if (paymentResults["status"] == "COMPLETED") {
             displayPaymentResults('SUCCESS');
             alert("Thank you for your purchase.\n Your payment was processed successfully.\n An email has been sent for confirmation. ")

             console.debug('Payment Success', paymentResults);
         }
         else{
            alert('Maximum payment tries exceeded. Unable to process payment.')
         }
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
        await handlePaymentMethodSubmission(event, card);
    });

});

// Call this function to send a payment token, buyer name, and other details
// to the project server code so that a payment can be created with
// Payments API
async function createPayment(token) {
//    $("#sq_token").val(token);
//    $('#payment-form').submit();

    var paymentResponse = await $.post("payment", {
        sq_token: token,
        csrfmiddlewaretoken: $('[name="csrfmiddlewaretoken"]').val()
        }, function(data, status){
            return data;
            }, "json");
    if (paymentResponse["status"] == "COMPLETED") {
        $("#receipt").show();
        $("#receipt").attr("href", paymentResponse["receipt_url"]);
        $("#index-link").show();
        }
    else if (!paymentResponse["continue"]){
        alert(paymentResponse["error"]);
    }
    else {
        alert(paymentResponse["error"]);
        throw new Error(paymentResponse["error"]);
        }
    return paymentResponse;
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

// Helper method for displaying the Payment Status on the screen.
// status is either SUCCESS or FAILURE;
function displayPaymentResults(status) {
const statusContainer = document.getElementById(
 'payment-status-container'
);
if (status === 'SUCCESS') {
 statusContainer.classList.remove('is-failure');
 statusContainer.classList.add('is-success');
} else {
 statusContainer.classList.remove('is-success');
 statusContainer.classList.add('is-failure');
}

statusContainer.style.visibility = 'visible';
}


//$(document).ready(function() {
//    if ($('#message').html() != "") {
//        alert($('#message').html());
//    };
//
//});
