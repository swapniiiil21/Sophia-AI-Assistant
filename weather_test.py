import requests

def get_weather(city):
    api_key = "75770f09e08718e80aa7576528a9a3b1"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        if response.status_code == 200:
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            print(f"\n✅ Weather for {city.title()}:")
            print(f"   🌡️ Temperature: {temp}°C")
            print(f"   🌤️ Condition: {desc.capitalize()}")
        else:
            print(f"\n❌ City not found or API error: {data.get('message', 'Unknown error')}")
    except requests.exceptions.RequestException as e:
        print(f"\n🚫 Network error: {e}")

def main():
    while True:
        city = input("\nEnter a city name (or 'exit' to quit): ").strip()
        if city.lower() == 'exit':
            print("👋 Exiting weather test.")
            break
        if not city:
            print("⚠️ Please enter a valid city name.")
            continue
        get_weather(city)

if __name__ == "__main__":
    main()
