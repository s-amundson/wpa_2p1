$(document).ready(function() {
    var oTable = $('.datatable').dataTable({
        // ...
        "processing": true,
        "serverSide": true,
        "ajax": $("#student_table").attr("curl")
    });

});