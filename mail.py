import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart  # Многокомпонентный объект
from email.mime.text import MIMEText  # Текст/HTML
# Установка параметров подключения к SMTP-серверу
smtp_host = 'smtp.timeweb.ru'
smtp_port = 465
# Создание объекта SMTP-клиента
smtp_client = smtplib.SMTP_SSL(smtp_host, smtp_port)
# Указание учетных данных для аутентификации
smtp_username = 'info@hibots.ru'
smtp_password = ''
smtp_client.login(smtp_username, smtp_password)
# Создание объекта сообщения
msg = MIMEMultipart()  # Создаем сообщение
msg['Subject'] = 'Тестовое сообщение'
msg['From'] = 'info@hibots.ru'
msg['To'] = 'vladchpok@gmail.com'
email_msg = '''<!DOCTYPE html> <html> <head> <meta charset="utf-8"> 
<title>Подтверждение регистрации аккаунта</title> 
</head> <body> <img src="static/images/Group 3logo.svg" alt="Логотип компании"> 
<h1>Уважаемый пользователь!</h1> 
<p>Перейдите по следующей ссылке для подтверждения регистрации аккаунта на FastStep.ru.</p> 
<p>Для защиты данных не передавайте этот код никому.</p> <p>Если Вы не делали этот запрос, проигнорируйте это сообщение.</p>
<p>С уважением,</p> <p>FastStep</p> </body> </html>
'''
msg.attach(MIMEText(email_msg, 'html'))  # Добавляем в сообщение текст
# Отправка сообщения через SSL-защищенное соединение
smtp_client.send_message(msg)
print('Письмо успешно отправлено')
# Закрытие соединения с SMTP-сервером
smtp_client.quit()