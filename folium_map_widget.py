from PyQt6.QtWebEngineWidgets import QWebEngineView
import folium
from folium import plugins
import json


class MapWidget(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_coords = []
        self.map = self.create_map()
        self.map.save("map.html")
        self.setHtml(self.map.get_root().render())

    def create_map(self, country_iso):
        with open("country_outlines/countries.geojson") as handle:
            country_outlines = json.loads(handle.read())

        with open("country_outlines/countries_centroids.geojson") as handle:
            country_centroids = json.loads(handle.read())

        for i in country_outlines["features"]:
            if i["properties"]["ISO3166-1-Alpha-2"] == country_iso.upper():
                country_outline = i
                break

        self.current_coords = country_outline["geometry"]["coordinates"]
        if country_outline["geometry"]["type"] == "Polygon":
            self.current_coords = [self.current_coords]

        if country_iso.lower() in ["ru", "nz", "fj"]:
            country_outline = self.shift_russia(country_outline)
        if country_iso.lower() in "us":
            country_outline = self.shift_usa(country_outline)

        xmin = ymin = float("inf")
        xmax = ymax = float("-inf")
        for part in self.current_coords:
            for p in part:
                lons = [point[0] for point in p]
                lats = [point[1] for point in p]
                xmin, xmax = min(xmin, min(lons)), max(xmax, max(lons))
                ymin, ymax = min(ymin, min(lats)), max(ymax, max(lats))

        for i in country_centroids["features"]:
            if i["properties"]["ISO"] == country_iso.upper():
                country_centroid = i["geometry"]["coordinates"]
                country_centroid.reverse()
                break

        m = folium.Map(
            location=country_centroid,
            min_zoom=1,
            max_zoom=20,
            crs="EPSG3857",
        )

        m.fit_bounds([[ymin, xmin], [ymax, xmax]])
        folium.GeoJson(
            country_outline,
            name=country_outline["properties"]["name"],
            style_function=lambda feature: {"weight": 1},
        ).add_to(m)
        folium.LayerControl().add_to(m)
        folium.Marker(country_centroid, popup=country_outline["properties"]["name"], icon=folium.Icon(color="red")).add_to(m)

        plugins.Fullscreen().add_to(m)
        plugins.LocateControl().add_to(m)

        return m

    def shift_usa(self, country_outline):
        for part in self.current_coords:
            for p in part:
                for point in p:
                    point[0] -= 340
                    point[0] = point[0] % 360
                    point[0] -= 380
        return country_outline

    def shift_russia(self, country_outline):
        for part in self.current_coords:
            for p in part:
                for point in p:
                    point[0] -= 340
                    point[0] = point[0] % 360
                    point[0] -= 20
        return country_outline
