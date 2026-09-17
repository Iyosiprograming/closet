import requests

from app.Core.logger import logger


def get_weather(
    location: str | None,
    openweather_api_key: str | None,
) -> str:
    if not location:
        logger.info("Weather skipped because user location is not set")
        return "Weather information unavailable"

    if not openweather_api_key:
        logger.info("Weather skipped because OpenWeather API key is not set")
        return "Weather information unavailable"

    try:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "q": location,
                "appid": openweather_api_key,
                "units": "metric",
            },
            timeout=10,
        )

        response.raise_for_status()
        data = response.json()

        temperature = data["main"]["temp"]
        description = data["weather"][0]["description"]

        return f"{temperature}°C, {description}"

    except requests.exceptions.Timeout:
        logger.warning(
            "Weather API timed out for location: %s",
            location,
        )
        return "Weather information unavailable"

    except requests.exceptions.RequestException as exc:
        logger.warning(
            "Weather API request failed for %s: %s",
            location,
            exc,
        )
        return "Weather information unavailable"

    except (KeyError, IndexError, TypeError, ValueError) as exc:
        logger.warning(
            "Unexpected weather API response for %s: %s",
            location,
            exc,
        )
        return "Weather information unavailable"