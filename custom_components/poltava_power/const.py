"""Constants for Poltava Power Outages integration."""

DOMAIN = "poltava_power"
NAME = "Полтаваобленерго ГПВ"
ATTRIBUTION = "Дані надано АТ 'ПОЛТАВАОБЛЕНЕРГО' (парсинг OE_OUTAGE_DATA)"

CONF_QUEUE = "queue"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_INCLUDE_POSSIBLE = "include_possible"
CONF_DATA_URL = "data_url"

DEFAULT_QUEUE = "3.1"
DEFAULT_UPDATE_INTERVAL = 5  # minutes
DEFAULT_INCLUDE_POSSIBLE = False
DEFAULT_DATA_URL = (
    "https://raw.githubusercontent.com/yaroslav2901/OE_OUTAGE_DATA/main/data/Poltavaoblenergo.json"
)
IMAGE_BASE_URL = (
    "https://raw.githubusercontent.com/yaroslav2901/OE_OUTAGE_DATA/main/images/Poltavaoblenergo/"
)

# Poltava Oblenergo queues (6 main queues, 2 subqueues each)
QUEUES = {
    "1.1": "Черга 1, підчерга 1 (1.1)",
    "1.2": "Черга 1, підчерга 2 (1.2)",
    "2.1": "Черга 2, підчерга 1 (2.1)",
    "2.2": "Черга 2, підчерга 2 (2.2)",
    "3.1": "Черга 3, підчерга 1 (3.1)",
    "3.2": "Черга 3, підчерга 2 (3.2)",
    "4.1": "Черга 4, підчерга 1 (4.1)",
    "4.2": "Черга 4, підчерга 2 (4.2)",
    "5.1": "Черга 5, підчерга 1 (5.1)",
    "5.2": "Черга 5, підчерга 2 (5.2)",
    "6.1": "Черга 6, підчерга 1 (6.1)",
    "6.2": "Черга 6, підчерга 2 (6.2)",
}

# Image file name mapping for each queue
QUEUE_IMAGE_FILES = {
    "1.1": "gpv-1-1-emergency.png",
    "1.2": "gpv-1-2-emergency.png",
    "2.1": "gpv-2-1-emergency.png",
    "2.2": "gpv-2-2-emergency.png",
    "3.1": "gpv-3-1-emergency.png",
    "3.2": "gpv-3-2-emergency.png",
    "4.1": "gpv-4-1-emergency.png",
    "4.2": "gpv-4-2-emergency.png",
    "5.1": "gpv-5-1-emergency.png",
    "5.2": "gpv-5-2-emergency.png",
    "6.1": "gpv-6-1-emergency.png",
    "6.2": "gpv-6-2-emergency.png",
}

IMAGE_ALL_TODAY = "gpv-all-today.png"
IMAGE_ALL_TOMORROW = "gpv-all-tomorrow.png"

# Outage raw states translation
STATUS_DESCRIPTIONS = {
    "yes": "Світло є",
    "no": "Світла немає (Відключення)",
    "first": "Світла немає перші 30 хв",
    "second": "Світла немає другі 30 хв",
    "mfirst": "Можливе відключення перші 30 хв",
    "msecond": "Можливе відключення другі 30 хв",
}

STATE_POWER_ON = "power_on"
STATE_POWER_OFF = "power_off"
STATE_MAYBE_OFF = "maybe_off"
