$(document).ready(function() {
    console.log('loaded')
	var sig = $('#sig').signature();
	$('#disable').click(function() {
		var disable = $(this).text() === 'Disable';
		$(this).text(disable ? 'Enable' : 'Disable');
		sig.signature(disable ? 'disable' : 'enable');
	});
	$('#clear').click(function() {
		sig.signature('clear');
	});
	$('#json').click(function() {
		alert(sig.signature('toJSON'));
	});
	$('#svg').click(function() {
		alert(sig.signature('toSVG'));
	});
	$("#sign_in_form").submit(function(e){
        e.preventDefault();
        console.log('submit')
        $("#id_signature").val(sig.signature('toDataURL', 'image/jpeg', 0.8));
        $(this).unbind();
        $(this).submit();
    });
});