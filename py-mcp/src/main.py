import httpx
from fastmcp import FastMCP

mcp = FastMCP("Weather")

WTTR_URL = "https://wttr.in"


def _get_weather_data(city: str) -> dict:
    resp = httpx.get(f"{WTTR_URL}/{city}", params={"format": "j1"}, timeout=10)
    resp.raise_for_status()
    return resp.json()


@mcp.tool()
def get_weather(city: str) -> str:
    data = _get_weather_data(city)
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


@mcp.tool()
def get_forecast(city: str) -> str:
    data = _get_weather_data(city)
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


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
