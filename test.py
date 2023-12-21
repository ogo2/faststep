from datetime import datetime

now = datetime.today()
formatted_date = datetime.strftime(datetime.now(), '%d/%m/%Y')
print(type(now))
print(now)