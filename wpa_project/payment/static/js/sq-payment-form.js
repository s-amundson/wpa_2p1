
async function initializeCard(payments) {
 const card = await payments.card();
 await card.attach('#card-container');
 return card;
}

document.addEventListener('DOMContentLoaded', async function () {
    $("#receipt").hide();
    $("#index-link").hide();
    console.log(window.action_url)
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
             alert_notice("Success", "Thank you for your purchase.\n Your payment was processed successfully.\n An email has been sent for confirmation. ")

         }
         else{
            alert_notice("Error", 'Maximum payment tries exceeded. Unable to process payment.')
         }
       } catch (e) {
         cardButton.disabled = false;
         displayPaymentResults('FAILURE');
         console.error(e.message);
       }
 }
    var cost_no_donation = parseFloat($("#total-div").html());
    $("#donation").change(function () {
        console.log($("#donation").val())
        if ($("#donation").val() < 0 ){
            $("#donation").val(0)
        }
        $("#total-div").html(cost_no_donation + parseFloat($("#donation").val()));
    });

    const cardButton = document.getElementById(
        'card-button'
    );
    cardButton.addEventListener('click', async function (event) {
        if(cost_no_donation + parseFloat($("#donation").val()) > 0) {
            await handlePaymentMethodSubmission(event, card);
        }
        else {
            await createPayment('no-payment')
        }
    });
    $("#payment-form").submit(function(e){
        e.preventDefault();
        createPayment('no-payment')
    });
});

// Call this function to send a payment token, buyer name, and other details
// to the project server code so that a payment can be created with
// Payments API
async function createPayment(token) {
//    $("#sq_token").val(token);
//    $('#payment-form').submit();

    var paymentResponse = await $.post(window.action_url, {
        sq_token: token,
        csrfmiddlewaretoken: $('[name="csrfmiddlewaretoken"]').val(),
        donation: $("#donation").val(),
        note: $("#id_note").val()
        }, function(data, status){
            return data;
            }, "json");
    if (paymentResponse["status"] == "COMPLETED") {
        $("#receipt").show();
        $("#receipt").attr("href", paymentResponse["receipt_url"]);
        $("#index-link").show();
        }
    else if (!paymentResponse["continue"]){
        alert_notice('Notice', paymentResponse["error"]);
    }
    else {
        alert_notice("Notice", paymentResponse["error"]);
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
