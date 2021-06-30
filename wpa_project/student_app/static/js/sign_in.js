$(document).ready(function() {
    console.log('loaded')
	var sig = $('#sig').signature();

    $("#btn-submit").prop('disabled', true);
    sig.signature({
    change: function(event, ui) {
        if (sig.signature('isEmpty')) {
            console.log('sig empty');
            $("#btn-submit").prop('disabled', true);
        }
        else {
            $("#btn-submit").prop('disabled', false);
        }
    }});
	$('#clear').click(function(e) {
	    e.preventDefault();
		sig.signature('clear');
	});
	$('#json').click(function() {
		alert(sig.signature('toJSON'));
	});
	$('#svg').click(function() {
		alert(sig.signature('toSVG'));
	});
	$("#sign_in_form").submit(function(e) {
	    e.preventDefault();
	    if (!sig.signature('isEmpty')) {
            console.log('submit')
            $("#id_signature").val(sig.signature('toDataURL', 'image/jpeg', 0.8));
            $(this).unbind();
            $(this).submit();
            }
        });
//	$("#btn-submit").click(form_submit);
});
