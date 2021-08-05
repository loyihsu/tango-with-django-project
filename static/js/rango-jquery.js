$(document).ready(function() {
    $('#about-btn').click(function() {
        alert('You clicked the button using JQuery!');
    });
    $('.ouch').click(function() {
        alert('You clicked me! Ouch!');
    });
    $('p').hover( function() {
        $(this).css('color', 'red');
    }, function() {
        $(this).css('color', 'black');
    });

    $("#about-btn").removeClass('btn-primary').addClass('btn-success');

    $('#about-btn').click(function() {
        msgStr = $('#msg').html();
        msgStr = msgStr + ' ooo, fancy!';
        $('#msg').html(msgStr);
    });

    $('#like_btn').click(function() {
        var catecategoryIdVar;
        catecategoryIdVar = $(this).attr('data-categoryid');
        
        $.get('/rango/like_category/',
            {'category_id': catecategoryIdVar},
            function(data) {
                $('#like_count').html(data);
                $('#like_btn').hide();
        });
    });

    $('#search-input').keyup(function() { var query;
        query = $(this).val();
            $.get('/rango/suggest/', {'suggestion': query},
        function(data) {
            $('#categories-listing').html(data);
        })
    });   
});
