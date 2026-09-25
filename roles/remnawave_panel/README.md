# remnawave_panel

Разворачивает control plane Remnawave на Debian/Ubuntu:

- официальный контейнер `remnawave/backend:3`;
- PostgreSQL и Valkey из production Compose upstream;
- постоянные случайные секреты в `/opt/remnawave/.secrets`;
- Nginx и сертификат Let's Encrypt;
- локальные биндинги Panel, Metrics и PostgreSQL.

Обязательные переменные:

- `remnawave_panel_domain` — домен без `http://`, `https://` и пути;
- `remnawave_panel_acme_email` — email для Let's Encrypt.

DNS A/AAAA-запись должна указывать на control plane до запуска роли. Входящие
TCP 80 и 443 должны быть доступны для ACME и клиентов.

Секреты можно передать через Ansible Vault переменными
`remnawave_panel_app_secret`, `remnawave_panel_metrics_password`,
`remnawave_panel_webhook_secret`, `remnawave_panel_postgres_password`.
Если значения пусты, роль генерирует их один раз и повторно использует при
следующих запусках.
