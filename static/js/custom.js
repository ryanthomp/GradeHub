$(document).ready(function () 
{
    jQuery(document).ready(function($) 
	{
        $(".table-secondary").click(function() 
		{
            window.location = $(this).data("href");
        });
		$(".card").click(function () 
		{
            window.location = $(this).data("href");
        });
		$(".table-info").click(function () 
		{
            window.location = $(this).data("href");
		});
        $(".table-warning").click(function () {
            window.location = $(this).data("href");
        });
        $(".table-danger").click(function () 
		{
            window.location = $(this).data("href");
        });
        $(".table-success").click(function () 
		{
            window.location = $(this).data("href");
        });
        $(".alert-info").click(function () 
		{
            window.location = $(this).data("href");
        });
    });     
});
