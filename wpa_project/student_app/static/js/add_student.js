
$(document).ready(function() {

    $("#add-student").modalForm({
        formURL: "{% url 'add_student' %}"
    });

});
