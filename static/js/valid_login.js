$(document).ready(function() {
    $('#submit_login').on('click', function(event){
        event.preventDefault();
        var email = $('#email').val();
        var password = $('#password').val();

        $.ajax({
            url: '/login',
            method: 'post',
            dataType: 'json',
            contentType: 'application/json',
            data: JSON.stringify({'email': email, 'password': password}),
            success: function(data){
                window.location.href = "/shoes"; // Выполнить редирект на новую страницу
            },
            error: function(error){
                console.log(error)
            }
        })
    })

})