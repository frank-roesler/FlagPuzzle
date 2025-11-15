from flask import Flask, render_template, session, redirect, url_for
import folium
import json
import random
import os

app = Flask(__name__)
app.secret_key = "replace_this_with_a_random_secret"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FLAGS_FOLDER = os.path.join(BASE_DIR, "country-flags-main", "png")
GEOJSON_FILE = os.path.join(BASE_DIR, "country_outlines", "countries.geojson")
COUNTRIES_JSON = os.path.join(BASE_DIR, "country-flags-main", "countries.json")

# Load country names
with open(COUNTRIES_JSON, "r", encoding="utf-8") as f:
    COUNTRIES = {k.lower(): v for k, v in json.load(f).items()}

# Load GeoJSON
with open(GEOJSON_FILE, "r", encoding="utf-8") as f:
    GEOJSON = json.load(f)


def get_country_coords(country_iso):
    """Return GeoJSON coordinates for a country"""
    for feature in GEOJSON["features"]:
        if feature["properties"]["ISO3166-1-Alpha-2"].upper() == country_iso.upper():
            coords = feature["geometry"]["coordinates"]
            if feature["geometry"]["type"] == "Polygon":
                coords = [coords]
            # Apply shifts if needed
            if country_iso.lower() in ["ru", "nz", "fj"]:
                coords = shift_russia(coords)
            if country_iso.lower() == "us":
                coords = shift_usa(coords)

            xmin = ymin = float("inf")
            xmax = ymax = float("-inf")
            for part in coords:
                for p in part:
                    lons = [point[0] for point in p]
                    lats = [point[1] for point in p]
                    xmin, xmax = min(xmin, min(lons)), max(xmax, max(lons))
                    ymin, ymax = min(ymin, min(lats)), max(ymax, max(lats))
            return coords, (xmin, xmax, ymin, ymax)
    return []


def shift_usa(coords):
    for part in coords:
        for poly in part:
            for point in poly:
                point[0] -= 340
                point[0] = point[0] % 360
                point[0] -= 380
    return coords


def shift_russia(coords):
    for part in coords:
        for poly in part:
            for point in poly:
                point[0] -= 340
                point[0] = point[0] % 360
                point[0] -= 20
    return coords


def generate_map(country_iso):
    coords_list, (xmin, xmax, ymin, ymax) = get_country_coords(country_iso)
    if not coords_list:
        return "<p>Map not found</p>"

    # Center map on first point
    first = coords_list[0][0][0]
    m = folium.Map(location=[first[1], first[0]], zoom_start=5, tiles="cartodb positron")
    m.fit_bounds([[ymin, xmin], [ymax, xmax]])
    for polygon in coords_list:
        for poly in polygon:
            folium.Polygon(locations=[(pt[1], pt[0]) for pt in poly], color="blue", weight=2, fill=True, fill_color="#55ff00").add_to(m)

    return m._repr_html_()


def init_session():
    if "remaining_countries" not in session:
        session["remaining_countries"] = list(COUNTRIES.keys())
        session["current_country"] = None


@app.route("/")
def index():
    init_session()
    return redirect(url_for("next_country"))


@app.route("/next")
def next_country():
    init_session()
    if not session["remaining_countries"]:
        return "<h1>All countries completed!</h1>"
    country_iso = random.choice(session["remaining_countries"])
    session["current_country"] = country_iso
    flag_path = f"/static/flags/{country_iso}.png"
    country_name = COUNTRIES[country_iso]
    session.modified = True
    # Do NOT generate map yet
    map_html = ""
    return render_template("index.html", flag_path=flag_path, map_html=map_html, country_name=country_name, revealed=False, remaining=len(session["remaining_countries"]))


@app.route("/reveal")
def reveal():
    init_session()
    country_iso = session.get("current_country")
    if not country_iso:
        return redirect(url_for("next_country"))
    map_html = generate_map(country_iso)
    flag_path = f"/static/flags/{country_iso}.png"
    country_name = COUNTRIES[country_iso]
    return render_template("index.html", flag_path=flag_path, map_html=map_html, country_name=country_name, revealed=True, remaining=len(session["remaining_countries"]))


@app.route("/remove")
def remove():
    init_session()
    country_iso = session.get("current_country")
    if country_iso and country_iso in session["remaining_countries"]:
        session["remaining_countries"].remove(country_iso)
        session.modified = True
    return redirect(url_for("next_country"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
