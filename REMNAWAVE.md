# Remnawave: один control plane и несколько dataplane

## Архитектура

```text
Internet
   |
   | TCP 443/80
   v
control-1 (Panel + Nginx + PostgreSQL + Valkey)
   |
   | TCP 2222, разрешён только от control-1
   +----------------------+----------------------+
   v                      v                      v
node-1 (Xray)         node-2 (Xray)         node-N (Xray)
   ^                      ^                      ^
   +--------- клиентские Xray inbound-порты -----+
```

Panel не содержит Xray-core. Каждый dataplane запускает отдельный Remnawave
Node и получает конфигурацию от control plane.

## Требования

- Control plane: Debian/Ubuntu, минимум 2 CPU, 2 GB RAM, 20 GB диска;
  рекомендуется 4 CPU и 4 GB RAM.
- Dataplane: Debian/Ubuntu, минимум 1 CPU и 1 GB RAM.
- DNS A/AAAA-запись домена панели должна указывать на control plane.
- Control plane: открыть TCP 22, 80 и 443.
- Dataplane: открыть SSH; TCP 2222 (или выбранный `remnawave_node_port`)
  разрешить только от IP control plane; клиентские Xray-порты открыть отдельно.
- На управляющей машине нужны Ansible 2.14+ и SSH-доступ к серверам.

Роли устанавливают Docker Engine и Docker Compose plugin из официального
репозитория Docker.

## Подготовка inventory

```bash
cp inventory/remnawave.example.yml inventory/remnawave.yml
```

Заполните IP-адреса, SSH-параметры, домен и email. Файл
`inventory/remnawave.yml` исключён из Git и предназначен для приватных
значений.

## Этап 1 — control plane

```bash
ansible-playbook -i inventory/remnawave.yml remnawave.yml \
  --limit remnawave_control
```

После завершения откройте `https://<ваш-домен>/`. Первый зарегистрированный
пользователь становится super-admin.

## Этап 2 — dataplane

Для каждого сервера в Panel откройте **Nodes → Management**, создайте узел с
тем же портом, который указан в inventory, и скопируйте `SECRET_KEY` из
сгенерированного Compose. У каждого узла должен быть свой секрет.

Запишите секреты в `remnawave_node_secret` соответствующих hosts и запустите:

```bash
ansible-playbook -i inventory/remnawave.yml remnawave.yml \
  --limit remnawave_nodes
```

После этого завершите создание узла в Panel и назначьте ему Config Profile.

### Временная совместимость с Ubuntu 20.04

Для `node-2` с системным Python 3.8 запускайте playbook под отдельным
`ansible-core 2.19.13` (контроллер использует Python 3.13):

```bash
uvx --python 3.13 --from 'ansible-core==2.19.13' \
  ansible-playbook -i inventory/remnawave.yml remnawave.yml --limit node-2
```

Обычный Ansible 2.20 требует Python 3.9+ на целевом сервере. Этот запуск не
обновляет системный Ansible и не затрагивает остальные хосты. Ubuntu 20.04 уже
не входит в список официально поддерживаемых Docker Engine систем; при первой
возможности пересоздайте ноду на актуальной Ubuntu.

## Повторный запуск и обновление

Обе роли идемпотентны относительно конфигурации и постоянных данных. Для
применения новых image-тегов измените переменные image в inventory и повторите
playbook. Обновлять рекомендуется сначала Panel, затем Nodes.

```bash
ansible-playbook -i inventory/remnawave.yml remnawave.yml
```

Перед обновлением PostgreSQL между major-версиями сделайте резервную копию.
Роль сохраняет данные в Docker volume `remnawave-db-data`, но сама backup и
major migration не выполняет.

## Секреты

Автоматически созданные секреты control plane хранятся только на сервере в
`/opt/remnawave/.secrets` с правами `0600`. Файл окружения также имеет
`0600`. Чтобы управлять секретами самостоятельно, задайте соответствующие
переменные через Ansible Vault.

Node `SECRET_KEY` находится в приватном inventory. Не коммитьте реальный
inventory и не используйте один Node secret на нескольких серверах.
