# OpenVPN RUS

Репозиторий для управления OpenVPN-сервером `217.18.60.199` через `Makefile` и `Ansible`.

## Что делает этот репозиторий

- поднимает и настраивает OpenVPN на сервере;
- выпускает клиентские сертификаты;
- перевыпускает клиентские сертификаты;
- отзывает клиентские сертификаты;
- собирает готовые `.ovpn` профили локально в `clients/rus/`.

## Быстрый старт

Рабочая директория:

```bash
cd /home/sekarpov/my-projects/openvpn-rus
```

Основная команда всегда запускается отсюда.

## Какие файлы важны

- `Makefile` — точка входа для всех команд
- `provisioning/inventories/production/hosts.yml` — сервер для подключения по SSH
- `provisioning/inventories/production/group_vars/all.yml` — параметры OpenVPN
- `clients/rus/` — готовые клиентские `.ovpn` файлы

## Обязательные параметры

У большинства команд используются два параметра:

- `INVENTORY=production` — какой inventory использовать
- `CLIENT=<имя_клиента>` — имя клиента, если команда работает с клиентским сертификатом

Если команда не работает с клиентом, `CLIENT` не нужен.

## Команды

### Проверить состояние сервера

Показывает статус OpenVPN и сводку по PKI.

```bash
make status INVENTORY=production
```

### Поднять или обновить сервер

Применяет текущий provisioning к серверу.

```bash
make provision INVENTORY=production
```

### Посмотреть список клиентов

Показывает список клиентских сертификатов из PKI.

```bash
make list-clients INVENTORY=production
```

### Выпустить новый клиент

Создаёт новый клиентский сертификат и готовый `.ovpn`.

```bash
make client-create INVENTORY=production CLIENT=client_name
```

Результат:

```bash
clients/rus/client_name.ovpn
```

### Пересобрать существующий `.ovpn`

Не перевыпускает сертификат. Просто заново собирает локальный `.ovpn` из текущих файлов PKI.

```bash
make client-config INVENTORY=production CLIENT=client_name
```

Когда использовать:

- если сертификат уже существует;
- если нужно просто получить `.ovpn` заново;
- если предыдущий запуск не успел пересобрать локальный файл.

### Перевыпустить клиентский сертификат

Отзывает текущий сертификат клиента, выпускает новый и пересобирает `.ovpn`.

```bash
make client-renew INVENTORY=production CLIENT=client_name
```

Алиас той же команды:

```bash
make client-rotate INVENTORY=production CLIENT=client_name
```

Когда использовать:

- если ключ клиента скомпрометирован;
- если нужно выдать новый сертификат с тем же именем клиента;
- если старый профиль надо заменить полностью.

### Отозвать клиента

Отзывает сертификат клиента и убирает локальный `.ovpn` в архив отозванных.

```bash
make client-revoke INVENTORY=production CLIENT=client_name
```

### Перевыпустить сертификат сервера

Перевыпускает серверный сертификат с тем же CN.

```bash
make server-renew INVENTORY=production
```

## Самые частые сценарии

### Создать нового клиента

```bash
cd /home/sekarpov/my-projects/openvpn-rus
make client-create INVENTORY=production CLIENT=client_name
```

### Перевыпустить клиента и получить новый `.ovpn`

```bash
cd /home/sekarpov/my-projects/openvpn-rus
make client-rotate INVENTORY=production CLIENT=client_name
```

### Если сертификат уже перевыпущен, но локальный `.ovpn` не собрался

```bash
cd /home/sekarpov/my-projects/openvpn-rus
make client-config INVENTORY=production CLIENT=client_name
```

### Проверить, что сервер вообще жив

```bash
cd /home/sekarpov/my-projects/openvpn-rus
make status INVENTORY=production
```

## Настройка клиента на Ubuntu

### 1. Подготовить клиентский профиль

Сначала создай или перевыпусти клиентский профиль в этом репозитории:

```bash
cd /home/sekarpov/my-projects/openvpn-rus
make client-create INVENTORY=production CLIENT=client_name
```

Если профиль уже был, но сертификат истёк или нужен новый ключ:

```bash
cd /home/sekarpov/my-projects/openvpn-rus
make client-renew INVENTORY=production CLIENT=client_name
```

Готовый файл появится здесь:

```bash
clients/rus/client_name.ovpn
```

### 2. Установить профиль в систему

Скопируй `.ovpn` в системную директорию OpenVPN:

```bash
sudo cp clients/rus/client_name.ovpn /etc/openvpn/client/client_name.ovpn
sudo chmod 600 /etc/openvpn/client/client_name.ovpn
```

Важно: unit в Ubuntu ожидает профиль именно по пути:

```bash
/etc/openvpn/client/client_name.ovpn
```

Если положить файл в другое место, например в `/etc/openvpn/client/rus/`, этот unit его не подхватит.

### 3. Запустить подключение

Запуск через systemd:

```bash
pkexec systemctl start openvpn-client-rus@client_name
```

Остановка:

```bash
pkexec systemctl stop openvpn-client-rus@client_name
```

Перезапуск после замены профиля:

```bash
pkexec systemctl restart openvpn-client-rus@client_name
```

### 4. Проверить, что VPN реально поднялся

Проверить статус сервиса:

```bash
systemctl status openvpn-client-rus@client_name --no-pager
```

Проверить лог:

```bash
journalctl -u openvpn-client-rus@client_name -n 50 --no-pager
```

Главный признак успешного подключения:

```text
Initialization Sequence Completed
```

Проверить интерфейс и маршруты:

```bash
ip -brief addr show tun0
ip route
```

При успешном подключении обычно видно:

- интерфейс `tun0` в состоянии `UP`;
- адрес из сети VPN, например `10.8.0.x/24`;
- маршруты `0.0.0.0/1` и `128.0.0.0/1` через `10.8.0.1`.

Проверить внешний IP:

```bash
curl ifconfig.me
```

Если VPN с `redirect-gateway` включён, внешний IP должен стать IP VPN-сервера, а не домашнего провайдера.

### 5. Если не подключается

Сначала смотри лог сервиса:

```bash
journalctl -u openvpn-client-rus@client_name -n 100 --no-pager
```

Частые признаки проблем:

- `TLS Error: TLS handshake failed` — соединение не завершило TLS-рукопожатие;
- `certificate has expired` — клиентский сертификат истёк, профиль нужно перевыпустить;
- нет строки `Initialization Sequence Completed` — VPN не поднялся до конца.

Для детальной диагностики можно запустить профиль вручную:

```bash
sudo openvpn --config /etc/openvpn/client/client_name.ovpn --verb 4
```

Если видишь предупреждение про истёкший сертификат, перевыпусти клиента:

```bash
cd /home/sekarpov/my-projects/openvpn-rus
make client-renew INVENTORY=production CLIENT=client_name
```

Потом замени системный `.ovpn` новым файлом и перезапусти сервис.

## Где искать результат

Все готовые клиентские файлы складываются сюда:

```bash
clients/rus/
```

Пример:

```bash
clients/rus/client_dasha_spb.ovpn
```

## Важно

- `.ovpn` содержит приватный ключ клиента, не коммить его в git.
- Если приватный ключ клиента утёк, используй `make client-rotate ...`.
- Для сервера `217.18.60.199` этот репозиторий уже настроен под текущий старый layout OpenVPN.
