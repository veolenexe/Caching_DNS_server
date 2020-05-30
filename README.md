# Caching_DNS_server

 Кэширующий DNS сервер. Сервер прослушивает 53 порт. При первом запуске кэш пустой. Сервер получает от клиента рекурсивный запрос и выполняет разрешение запроса. Получив ответ, сервер разбирает пакет ответа, извлекает из него ВСЮ полезную информацию, т. е. все ресурсные записи, а не только то, о чем спрашивал клиент. 
* Сервер регулярно просматривает кэш(ключ кэша: (доменное имя тип записи)) и удаляет просроченные записи (использует поле TTL).
Сервер не должен терять работоспособность (уходить в бесконечное ожидание, падать с
ошибкой и т. д.), если старший сервер почему-то не ответил на запрос. Во время штатного выключения сервер сериализует данные из кэша, сохраняет их на диск в cache.txt(при отсутствии файла создает его). При повторных запусках
сервер считывает данные с диска и удаляет просроченные записи, инициализирует таким образом свой кэш.
* отвечет на запросы : A, NS.
* Пример ввода:\npy dns_server.py
# Параметры:
отсутствуют
# Важно
* Автор Скрипченко Илья КН-202 МЕН 280207
