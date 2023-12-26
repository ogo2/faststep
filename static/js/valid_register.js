$(document).ready(function() {
    var email_val = false
    var password_val = false
    var password_repeat_val = false
    var phone_val = false
    var button = document.getElementById("submit_register");
    button.disabled = true;

    function valid_email(){
        var email = $('#email').val();
        if(validateEmail(email)) {
            $('#emailError').text('');
            email_val = true
        }if(email.length == 0){
            $('#emailError').text('');
            email_val = false
        }if (!validateEmail(email) && email.length > 0){
            email_val = false
            $('#emailError').text('Некорректный адрес электронной почты');
        }
        function validateEmail(email) {
            var re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return re.test(email);
        }
    }
    function repeat_password(){
        var password = $('#password').val();
        var password_repeat = $("#repeat_password").val();
        if (password_repeat != password) {
            password_repeat_val = false
            $('#error-message_repeat').text('Пароли не совпадают');
        } else {
            password_repeat_val = true
            $('#error-message_repeat').text('');
        }
    }
    function phone(){
        var phone = $('#phone-input').val();
        if (phone.length < 18){
            phone_val = false
            $('#error-message_phone').text('Введите номер телефона полностью');
        }if (phone.length == 0){
            phone_val = false
            $('#error-message_phone').text('');
        }if (phone.length==18){
            $('#error-message_phone').text('');
            phone_val = true
        }
    }
    function password_valid(){
        var password = $('#password').val();
        if (password.length < 8) {
            password_val = false
            $('#error-message').text('Пароль должен содержать не менее 8 символов');
        } else {
            password_val = true
            $('#error-message').text('');
        }
    }
    
    valid_email();
    phone();
    $('#password').on('input', function() {
        password_valid()
        });
    $('#repeat_password').on('input', function() {
        repeat_password()
        });
    
    $('#email').on('input', function() {
        valid_email();
        });
    
    // Получаем элемент input по его id
    var phoneInput = $('#phone-input');

    // Устанавливаем код страны при нажатии на поле ввода
    phoneInput.click(function() {
        // Проверяем, если код страны уже установлен, то не меняем его
        if (!phoneInput.val().startsWith('+7')) {
        phoneInput.val('+7');
        }
    });
    $('#phone-input').on('input', function() {
      var number = $(this).val().replace(/[^\d]/g, ''); // Удаляем все символы кроме цифр
      var formattedNumber = formatNumber(number); // Форматируем номер 
  
      $(this).val(formattedNumber); // Вставляем отформатированный номер обратно в поле ввода
      phone()    
    });
  
    function formatNumber(number) {
      var formattedNumber = '';
  
      if (number.length > 0) {
        formattedNumber += '+'; // Добавляем символ "+"
      }
  
      if (number.length >= 1) {
        formattedNumber += '7 '; // Добавляем код страны "7" с пробелом
      }
  
      if (number.length >= 2) {
        formattedNumber += '(' + number.substring(1, 4); // Добавляем открывающуюся скобку и первую цифру номера телефона
      }
  
      if (number.length >= 5) {
        formattedNumber += ') ' + number.substring(4, 7); // Добавляем закрывающуюся скобку и следующие 3 цифры номера телефона
      }
  
      if (number.length >= 8) {
        formattedNumber += '-' + number.substring(7, 9); // Добавляем тире и две последние цифры номера телефона
      }
  
      if (number.length >= 10) {
        formattedNumber += '-' + number.substring(9, 11); // Добавляем тире и две последние цифры номера телефона
      }
  
      return formattedNumber;
    }
    
    
    $('#submit_register').on('mouseenter', function() {
        if (email_val == true && password_val == true && password_repeat_val == true && phone_val == true){
            button.disabled = false;
            
    }});
    
    $('#submit_register').on('click', function(event){
        event.preventDefault();
        var password = $('#password').val();
        var email = $('#email').val();
        var phone = $('#phone-input').val();
        var remember = $('#remember_me').val();
        var name = $('#username').val();   
        remember = $("#remember_me").is(":checked")
        // remember = remember.toString()
        // remember = remember.charAt(0).toUpperCase() + remember.slice(1)
        $.ajax({
            url: '/register',
            method: 'post',
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({'name': name, 'email': email, "phone": phone, 'password': password, 'remember_me': remember}),
            success: function(data){
                console.log(data);
            },
            error: function(error){
                console.log(error);
            }
        })
    })
    
  });
  