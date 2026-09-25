# remnawave_node

Разворачивает dataplane Remnawave Node: host networking, `NET_ADMIN`,
высокий лимит открытых файлов и контейнер `remnawave/node`.

Обязательная переменная `remnawave_node_secret` уникальна для каждого узла.
Её нужно скопировать из Panel: **Nodes → Management → Add node → Copy
docker-compose.yml**.

Порт `remnawave_node_port` (по умолчанию 2222/TCP) должен быть разрешён в
firewall только с публичного IP control plane. Клиентские Xray-порты
разрешаются отдельно в соответствии с Config Profile.

## Локальный Nginx для Reality

При `remnawave_node_reality_nginx_enabled: true` роль:

1. проверяет, что A-запись домена уже указывает на IP ноды;
2. устанавливает Nginx и Certbot;
3. получает сертификат Let's Encrypt через HTTP-01 на внешнем порту 80;
4. поднимает TLS-сайт на Unix-сокете `/dev/shm/nginx.sock`;
5. монтирует общий `/dev/shm` в контейнер Remnawave Node;
6. включает автоматическое продление сертификата и безопасный reload Nginx;
7. проверяет HTTPS напрямую через Unix-сокет.

Пример host vars:

```yaml
remnawave_node_reality_nginx_enabled: true
remnawave_node_reality_domain: static-1.example.com
remnawave_node_reality_expected_ipv4: 203.0.113.20
remnawave_node_reality_acme_email: admin@example.com
```

После применения роли inbound в Remnawave Config Profile должен содержать:

```json
{
  "streamSettings": {
    "security": "reality",
    "realitySettings": {
      "target": "/dev/shm/nginx.sock",
      "xver": 1,
      "serverNames": ["static-1.example.com"]
    }
  }
}
```

В некоторых версиях Xray поле называется `dest` вместо `target`; сохраняйте
имя поля, которое уже использует валидатор вашей версии Remnawave/Xray.

Публичный порт 443 остаётся у Xray. Nginx принимает TLS только через локальный
Unix-сокет, поэтому отдельный TCP-порт для него не требуется.

Логи Xray можно писать в `/var/log/remnanode`; роль устанавливает logrotate.
