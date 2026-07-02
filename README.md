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
