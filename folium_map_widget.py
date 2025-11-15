import os
import sys
from PyQt6.QtWidgets import QSizePolicy
from PyQt6.QtWebEngineWidgets import QWebEngineView
from folium import Map, GeoJson
from json import loads


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller bundles"""
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class MapWidget(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_coords = []
        with open(resource_path("country_outlines/countries.geojson")) as handle:
            self.country_outlines = loads(handle.read())
        # with open(resource_path("country_outlines/countries_centroids.geojson")) as handle:
        #     self.country_centroids = loads(handle.read())
        self.update_map("de")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def update_map(self, country_iso):
        self.map = self.create_map(country_iso)
        self.map.save("map.html")
        self.setHtml(self.map.get_root().render())

    def create_map(self, country_iso):
        country_outline = None
        for i in self.country_outlines["features"]:
            if i["properties"]["ISO3166-1-Alpha-2"] == country_iso.upper():
                country_outline = i
                break
        if country_outline is None:
            raise ValueError(f"Country ISO code '{country_iso}' not found in outlines.")

        self.current_coords = country_outline["geometry"]["coordinates"]
        if country_outline["geometry"]["type"] == "Polygon":
            self.current_coords = [self.current_coords]

        if country_iso.lower() in ["ru", "nz", "fj", "ki"]:
            country_outline = self.shift_russia(country_outline)
        if country_iso.lower() in "us":
            country_outline = self.shift_usa(country_outline)
        # if country_iso.lower() in "mv":
        country_outline = self.shift_all(country_outline)

        xmin = ymin = float("inf")
        xmax = ymax = float("-inf")
        for part in self.current_coords:
            for p in part:
                lons = [point[0] for point in p]
                lats = [point[1] for point in p]
                xmin, xmax = min(xmin, min(lons)), max(xmax, max(lons))
                ymin, ymax = min(ymin, min(lats)), max(ymax, max(lats))

        # for i in self.country_centroids["features"]:
        #     if i["properties"]["ISO"] == country_iso.upper():
        #         country_centroid = i["geometry"]["coordinates"]
        #         country_centroid.reverse()
        #         break

        m = Map(
            min_zoom=1,
            max_zoom=20,
            tiles="cartodb positron",
        )

        m.fit_bounds([[ymin, xmin], [ymax, xmax]])
        GeoJson(
            country_outline,
            name=country_outline["properties"]["name"],
            style_function=lambda feature: {"weight": 1},
        ).add_to(m)
        # folium.LayerControl().add_to(m)
        # folium.Marker(country_centroid, popup=country_outline["properties"]["name"], icon=folium.Icon(color="red")).add_to(m)
        # plugins.LocateControl().add_to(m)

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

    def shift_all(self, country_outline):
        for part in self.current_coords:
            for p in part:
                for point in p:
                    point[0] += 2e-6
        return country_outline
