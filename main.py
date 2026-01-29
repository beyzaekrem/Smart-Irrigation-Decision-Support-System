import requests
import math

API_KEY = "03b355316ba8c38da288915abc1deb25"

LAT = 41.0082
LON = 28.9784

TARLA_ALANI_M2 = 500

# Anlık hava
current_url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"
current_data = requests.get(current_url).json()

temp = current_data["main"]["temp"]
humidity = current_data["main"]["humidity"]
wind_speed = current_data["wind"]["speed"]

# Saatlik tahmin
forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"
forecast_data = requests.get(forecast_url).json()

def calculate_et0(temp, humidity, wind_speed):
    et0 = (0.408 * temp) + (0.54 * wind_speed) - (0.3 * (humidity / 100))
    return round(et0, 2)

et0 = calculate_et0(temp, humidity, wind_speed)
su_ihtiyaci_litre = round(et0 * TARLA_ALANI_M2, 1)

print("\n📍 Şehir:", current_data["name"])
print("🌡 Sıcaklık:", temp, "°C")
print("💧 Nem:", humidity, "%")
print("🌬 Rüzgar Hızı:", wind_speed, "m/s")
print("💦 Günlük Su Kaybı (ET0):", et0, "mm")
print("🚿 Önerilen Sulama Miktarı:", su_ihtiyaci_litre, "litre")

# En iyi saat seçimi
best_hour = None
best_score = 999

print("\n🕒 Saatlik Sulama Uygunluğu Analizi:")

for hour in forecast_data["list"][:8]:
    hour_time = hour["dt_txt"]
    t = hour["main"]["temp"]
    h = hour["main"]["humidity"]
    w = hour["wind"]["speed"]

    # Buharlaşma skoru (düşük daha iyi)
    score = t + (w * 2) - (h * 0.1)

    print(f"{hour_time} → Sıcaklık:{t}°C Nem:{h}% Rüzgar:{w} m/s | Skor:{round(score,2)}")

    if score < best_score:
        best_score = score
        best_hour = hour_time

print("\n EN UYGUN SULAMA SAATİ:", best_hour)

rain_expected = False

for hour in forecast_data["list"][:8]:
    if "rain" in hour:
        rain_expected = True

print("\n🌧 Yağmur Bekleniyor mu?:", "Evet" if rain_expected else "Hayır")

if et0 < 2:
    print("🛑 Sulama ÖNERİLMİYOR → Su ihtiyacı düşük")
elif rain_expected:
    print("🛑 Sulama ÖNERİLMİYOR → Yağmur bekleniyor")
else:
    print("✅ Sulama YAPILMALI → Optimal zaman:", best_hour)
