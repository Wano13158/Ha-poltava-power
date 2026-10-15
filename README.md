# ⚡ Полтаваобленерго ГПВ — Інтеграція для Home Assistant (HACS)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1+-blue.svg)](https://www.home-assistant.io/)
[![Maintainer](https://img.shields.io/badge/maintainer-grut123-orange.svg)](https://github.com/grut123)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Компактна та легка інтеграція для **Home Assistant** (з підтримкою **HACS**), що відображає актуальні **графіки погодинних відключень (ГПВ)** електроенергії в місті **Полтава та Полтавській області** (АТ «ПОЛТАВАОБЛЕНЕРГО»).

Підтримуються **всі черги та підчерги**:
* 🔹 **Черга 1:** `1.1`, `1.2`
* 🔹 **Черга 2:** `2.1`, `2.2`
* 🔹 **Черга 3:** `3.1`, `3.2`
* 🔹 **Черга 4:** `4.1`, `4.2`
* 🔹 **Черга 5:** `5.1`, `5.2`
* 🔹 **Черга 6:** `6.1`, `6.2`

---

## 🌟 Тільки потрібна інформація (без сміття на панелі)

За замовчуванням інтеграція активує **лише 3 найголовніших сенсори**, які не захаращують ваш інтерфейс:

1. **⚡ Поточний стан (`sensor.*_current_status`)**:
   * Показує: `Світло є`, `Відключення за графіком` або `Можливе відключення`.
2. **📅 Графік на сьогодні (`sensor.*_today_schedule`)**:
   * Зручний перелік годин без світла (наприклад: `10:00 - 11:00, 16:00 - 17:00, 22:00 - 23:00`).
3. **⏳ Наступне відключення (`sensor.*_next_outage`)**:
   * Зворотний відлік (наприклад: `Через 1 годину` або точний час початку).

> 💡 Всі допоміжні сутності (графічні картинки, календар, технічний час оновлення) **вимкнені за замовчуванням** і сховані в категорію «Діагностика». Якщо вони вам знадобляться, їх можна увімкнути в Налаштуваннях пристрою одним перемикачем.

---

## 📦 Встановлення

1. Скопіюйте теку `custom_components/poltava_power` у теку `config/custom_components/` вашого Home Assistant.
2. Перезавантажте Home Assistant.
3. Перейдіть до **Налаштування** ➡️ **Пристрої та служби** ➡️ **Додати інтеграцію**.
4. Знайдіть **Полтаваобленерго (ГПВ)** та оберіть вашу чергу (наприклад, **3.1**).

---

## 🎨 Приклади карток для дашборду

### 1. Компактна картка з 3 сенсорами (Entities card)

```yaml
type: entities
title: Світло Полтава (Черга 3.1)
show_header_toggle: false
entities:
  - entity: sensor.poltava_power_3_1_current_status
    name: Стан зараз
  - entity: sensor.poltava_power_3_1_next_outage
    name: Наступне відключення
  - entity: sensor.poltava_power_3_1_today_schedule
    name: Графік на сьогодні
```

### 2. 24-годинна кольорова шкала (Markdown card)

```yaml
type: markdown
title: Графік світла (Черга 3.1)
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
  <p style="margin-top: 10px; font-size: 14px;">
    <b>Сьогодні:</b> {{ states('sensor.poltava_power_3_1_today_schedule') }}
  </p>
  {% else %}
  Завантаження графіка...
  {% endif %}
```

---

## 📄 Ліцензія

MIT License. Дані парсяться з відкритих джерел проекту [OE_OUTAGE_DATA](https://github.com/yaroslav2901/OE_OUTAGE_DATA).
