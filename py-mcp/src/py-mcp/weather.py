import httpx

WTTR_URL = "https://wttr.in"

def get_weather_by_city(city: str) -> str:
    resp = httpx.get(f"{WTTR_URL}/{city}", params={"format": "j1"}, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    current = data["current_condition"][0]
    area = data["nearest_area"][0]
    name = area["areaName"][0]["value"]
    country = area["country"][0]["value"]

    return (
        f"🌍 {name}, {country}\n"
        f"🌡️ 温度: {current['temp_C']}°C\n"
        f"🤚 体感: {current['FeelsLikeC']}°C\n"
        f"💧 湿度: {current['humidity']}%\n"
        f"🌬️ 风速: {current['windspeedKmph']} km/h\n"
        f"🌀 气压: {current['pressure']} hPa\n"
        f"☁️ 天气: {current['weatherDesc'][0]['value']}"
    )


def get_forecast_by_city(city: str) -> str:
    resp = httpx.get(f"{WTTR_URL}/{city}", params={"format": "j1"}, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    area = data["nearest_area"][0]
    name = area["areaName"][0]["value"]
    country = area["country"][0]["value"]

    lines = [f"📅 {name}, {country} 天气预报"]
    for day in data["weather"]:
        date = day["date"]
        desc = day["hourly"][0]["weatherDesc"][0]["value"]
        lines.append(
            f"\n{date}: {desc}\n"
            f"  🌡️ {day['mintempC']}~{day['maxtempC']}°C\n"
            f"  ☀️ 日出 {day['astronomy'][0]['sunrise']}  🌅 日落 {day['astronomy'][0]['sunset']}"
        )
    return "\n".join(lines)
