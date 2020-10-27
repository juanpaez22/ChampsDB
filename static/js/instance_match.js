$(document).ready(function() {
    $('#stats').DataTable( {
        "order": [[ 8, "desc" ]],
        "paging":   false,
        "searching":   false,
        fixedHeader: true,
    } );
} );
