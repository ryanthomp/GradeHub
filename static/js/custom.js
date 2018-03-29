$(document).ready(function () {
    jQuery(document).ready(function($) {
        $(".table-secondary").click(function() {
            window.location = $(this).data("href");
        });
    });
});
