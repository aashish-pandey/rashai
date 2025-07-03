from fastapi import FastAPI, Query
from typing import Dict
import swisseph as swe
from datetime import datetime

app = FastAPI()

RASHIS = {
    1: "Aries", 2: "Taurus", 3: "Gemini", 4: "Cancer", 
    5: "Leo", 6: "Virgo", 7: "Libra", 8: "Scorpio",
    9: "Sagittarius", 10: "Capricorn", 11: "Aquarius", 
    12: "Pisces"
}

PLANETS = {
    0: "Sun", 1: "Moon", 2: "Mercury", 3: "Venus", 4: "Mars",
    5: "Jupiter", 6: "Saturn", 10: "Rahu", 11: "Ketu"
}

@app.get("/lagna-chart")
def generate_lagna_chart(
    year: int = Query(...),
    month: int = Query(...),
    day: int = Query(...),
    hour: float = Query(...),
    lat: float = Query(...),
    lon: float = Query(...)
) -> Dict:
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = swe.julday(year, month, day, hour)
    cusps, ascmc = swe.houses(jd, lat, lon)

    asc_degree = ascmc[0]
    asc_sign = int(asc_degree // 30) + 1

    house_signs = {}
    for i in range(12):
        degree = cusps[i]
        rashi = int(degree // 30) + 1
        house_signs[i+1] = rashi

    planet_positions = {}
    for pid in PLANETS:
        if pid == 11:
            rahu_data = swe.calc_ut(jd, 10)[0]
            lon_p = (rahu_data[0] + 180) % 360
        else:
            data = swe.calc_ut(jd, pid)[0]
            lon_p = data[0]

        rashi = int(lon_p // 30) + 1
        planet_positions[PLANETS[pid]] = {
            'longitude': lon_p,
            'rashi': rashi
        }

    def get_house_for_planet(degree, cusps):
        for i in range(12):
            start = cusps[i]
            end = cusps[(i+1)%12]
            if start < end:
                if start <= degree < end:
                    return i + 1
            else:
                if degree >= start or degree < end:
                    return i + 1
        return None

    for pname in planet_positions:
        degree = planet_positions[pname]['longitude']
        house = get_house_for_planet(degree, cusps)
        planet_positions[pname]['house'] = house
        planet_positions[pname]['house_rashi'] = house_signs[house]

    lagna_chart = {i: [] for i in range(1, 13)}
    for pname, pdata in planet_positions.items():
        lagna_chart[pdata['house']].append(pname)

    return {
        "ascendant": {
            "degree": asc_degree,
            "sign": RASHIS[asc_sign]
        },
        "house_signs": {str(k): RASHIS[v] for k, v in house_signs.items()},
        "lagna_chart": lagna_chart,
        "planet_positions": planet_positions
    }
