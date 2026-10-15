# ⚡ Полтаваобленерго ГПВ — Інтеграція для Home Assistant (HACS)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1+-blue.svg)](https://www.home-assistant.io/)
[![Maintainer](https://img.shields.io/badge/maintainer-grut123-orange.svg)](https://github.com/grut123)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Інтеграція для **Home Assistant** (з підтримкою **HACS**), що відображає актуальні **графіки погодинних відключень (ГПВ)** електроенергії в місті **Полтава та Полтавській області** (АТ «ПОЛТАВАОБЛЕНЕРГО»).

Підтримуються **всі черги та підчерги**:
* 🔹 **Черга 1:** `1.1`, `1.2`
* 🔹 **Черга 2:** `2.1`, `2.2`
* 🔹 **Черга 3:** `3.1`, `3.2`
* 🔹 **Черга 4:** `4.1`, `4.2`
* 🔹 **Черга 5:** `5.1`, `5.2`
* 🔹 **Черга 6:** `6.1`, `6.2`

---

## 🌟 Основні можливості

1. **⚡ Сенсор поточного стану живлення**:
   * Показує, чи є зараз світло за графіком: `Світло є`, `Відключення за графіком` або `Можливе відключення`.
   * Детальні атрибути з розбивкою по кожній годині доби.
2. **⏳ Точні таймери зворотної дії**:
   * **Наступне відключення (`sensor.*_next_outage`)**: точний час та дата початку відключення (з підтримкою `device_class: timestamp` для зворотного відліку на дашборді).
   * **Увімкнення світла (`sensor.*_next_restore`)**: коли очікується повернення електроенергії.
3. **📅 Зведені графіки на сьогодні та завтра**:
   * Зручний текстовий перелік періодів без світла (наприклад: `09:00 - 10:00, 15:00 - 16:00, 21:00 - 22:00`).
4. **📆 Вбудований календар Home Assistant (`calendar.*`)**:
   * Створює події відключень безпосередньо у рідному календарі Home Assistant.
   * Дозволяє налаштовувати нативні тригери автоматизацій за подіями календаря.
5. **🖼️ Офіційні графічні розклади (`image.*`)**:
   * Картинка графіка для вашої черги (`gpv-3-1-emergency.png`).
   * Загальна таблиця на сьогодні (`gpv-all-today.png`) та завтра (`gpv-all-tomorrow.png`).
6. **🔌 Бінарний сенсор (`binary_sensor.*`)**:
   * `device_class: power` — `on` (світло увімкнене), `off` (відключення).
7. **⚙️ Гнучке налаштування через UI**:
   * Вибір будь-якої черги.
   * Налаштування інтервалу оновлення (за замовчуванням 5 хв).
   * Опція врахування «можливих відключень» як обов'язкових.
   * Можливість додати кілька екземплярів (наприклад, окремо для дому, офісу та батьків).

---

## 📦 Встановлення

### Варіант 1: Через HACS (Рекомендовано)

1. Відкрийте **HACS** у вашому Home Assistant.
2. Перейдіть до розділу **Інтеграції** (Integrations).
3. Натисніть на меню з трьома крапками у правому верхньому кутку та виберіть **Користувацькі репозиторії** (Custom repositories).
4. Додайте посилання на цей репозиторій:
   * **URL:** `https://github.com/grut123/ha-poltava-power` (або ваш форк/репозиторій)
   * **Категорія:** `Інтеграція` (Integration)
5. Знайдіть у списку **Poltava Power Outages (Полтаваобленерго ГПВ)** та натисніть **Завантажити** (Download).
6. Перезавантажте Home Assistant.

### Варіант 2: Вручну

1. Скопіюйте теку `custom_components/poltava_power` у теку `config/custom_components/` вашого Home Assistant.
   Шлях має виглядати так:
   ```
   config/custom_components/poltava_power/
     ├── __init__.py
     ├── manifest.json
     ├── const.py
     ├── coordinator.py
     ├── config_flow.py
     ├── sensor.py
     ├── binary_sensor.py
     ├── calendar.py
     ├── image.py
     └── ...
   ```
2. Перезавантажте Home Assistant.

---

## ⚙️ Налаштування

1. У Home Assistant перейдіть до:
   **Налаштування** ➡️ **Пристрої та служби** ➡️ **Додати інтеграцію**.
2. Введіть у пошуку: **Полтаваобленерго** (або *Poltava Power*).
3. Оберіть вашу чергу (наприклад, **Черга 3, підчерга 1 (3.1)**).
4. Готово! Всі сенсори, календар та зображення графіка будуть створені автоматично.

> 💡 **Порада:** Якщо вам потрібно відстежувати кілька черг (наприклад, дім 3.1 та дача 1.2), просто додайте інтеграцію ще раз для іншої черги.

---

## 📊 Створені сутності (на прикладі черги 3.1)

| Сутність | Тип | Опис |
| :--- | :--- | :--- |
| `sensor.poltava_power_3_1_current_status` | Сенсор | Поточний стан: `Світло є`, `Відключення` тощо |
| `sensor.poltava_power_3_1_next_outage` | Timestamp | Дата та час наступного відключення |
| `sensor.poltava_power_3_1_next_restore` | Timestamp | Очікуваний час увімкнення світла |
| `sensor.poltava_power_3_1_today_schedule` | Сенсор | Список відключень на сьогодні (текст) |
| `sensor.poltava_power_3_1_tomorrow_schedule` | Сенсор | Список відключень на завтра (текст) |
| `sensor.poltava_power_3_1_last_update` | Сенсор | Час останнього оновлення обленерго |
| `binary_sensor.poltava_power_3_1_power_scheduled` | Binary Sensor | Наявність світла за планом (`on` / `off`) |
| `calendar.poltava_power_3_1` | Календар | Події розкладу відключень у календарі HA |
| `image.poltava_power_3_1_image_queue` | Зображення | Офіційна картинка графіка для черги 3.1 |
| `image.poltava_power_3_1_image_today` | Зображення | Зведена таблиця графіка для всіх черг на сьогодні |
| `image.poltava_power_3_1_image_tomorrow` | Зображення | Зведена таблиця на завтра |

---

## 🎨 Приклади карток для Lovelace Dashboards

### 1. Зручна 24-годинна кольорова шкала (Markdown Card)

Вставте цей код у картку типу **Markdown** вашого дашборду. Картка створить кольорову сітку на 24 години:
* 🟢 **Зелений** — світло є
* 🔴 **Червоний** — відключення
* 🟡 **Жовтий** — можливе відключення
* ⚪ **Біла рамка** — поточна година

```yaml
type: markdown
title: Графік світла Полтава (Черга 3.1)
content: >
  {% set hourly = state_attr('sensor.poltava_power_3_1_current_status', 'hourly_today') %}
  {% set cur_h = now().hour + 1 %}
  {% if hourly %}
  <div style="display: grid; grid-template-columns: repeat(12, 1fr); gap: 4px; text-align: center; font-size: 11px;">
  {% for h in range(1, 25) %}
    {% set val = hourly[h|string] or hourly[h] %}
    {% set is_cur = (h == cur_h) %}
    {% set bg = '#4CAF50' if val == 'yes' else ('#F44336' if val == 'no' else '#FF9800') %}
    {% set border = '2px solid #FFFFFF' if is_cur else 'none' %}
    <div style="background-color: {{ bg }}; color: white; padding: 6px 2px; border-radius: 4px; border: {{ border }}; font-weight: bold;">
      {{ '%02d' % (h-1) }}<br/>
      {% if val == 'yes' %}🟢{% elif val == 'no' %}🔴{% else %}🟡{% endif %}
    </div>
  {% endfor %}
  </div>
  <p style="margin-top: 10px; font-size: 13px;">
    <b>Сьогодні:</b> {{ states('sensor.poltava_power_3_1_today_schedule') }}<br/>
    <b>Завтра:</b> {{ states('sensor.poltava_power_3_1_tomorrow_schedule') }}
  </p>
  {% else %}
  Дані графіка завантажуються...
  {% endif %}
```

### 2. Картка з офіційним графіком (Picture Entity)

```yaml
type: picture-entity
entity: image.poltava_power_3_1_image_queue
name: Графік черги 3.1 від Полтаваобленерго
show_state: false
show_name: true
```

---

## 🔔 Приклади автоматизацій

### Сповіщення в телефон / Telegram за 30 хвилин до вимкнення:

```yaml
alias: "Полтава 3.1: Попередження про відключення"
description: "Надсилає сповіщення за 30 хвилин до планового вимкнення світла"
trigger:
  - platform: time
    at: sensor.poltava_power_3_1_next_outage
    offset: "-00:30:00"
action:
  - service: notify.notify
    data:
      title: "⚡ Увага! Відключення світла"
      message: "Через 30 хвилин (Черга 3.1) заплановано відключення електроенергії!"
```

### Автоматичне заряджання EcoFlow / Bluetti перед відключенням:

```yaml
alias: "Полтава 3.1: Зарядити зарядну станцію"
description: "Вмикає розетку станції за 1 годину до відключення"
trigger:
  - platform: time
    at: sensor.poltava_power_3_1_next_outage
    offset: "-01:00:00"
action:
  - service: switch.turn_on
    target:
      entity_id: switch.ecoflow_socket
```

---

## ℹ️ Джерело даних

Дані формуються на основі відкритих звітів АТ «ПОЛТАВАОБЛЕНЕРГО» та автоматично парсяться проектом [OE_OUTAGE_DATA](https://github.com/yaroslav2901/OE_OUTAGE_DATA) кожні 5 хвилин.

## 📄 Ліцензія

Проєкт розповсюджується під ліцензією [MIT](LICENSE).
