import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np


def scale_square(mp, xmin, ymin, xmax, ymax, factor):
    return (
        factor * (xmin - mp[0]) + mp[0],
        factor * (ymin - mp[1]) + mp[1],
        factor * (xmax - mp[0]) + mp[0],
        factor * (ymax - mp[1]) + mp[1],
    )


def get_minimal_square(xmin, ymin, xmax, ymax, world_bounds):
    min_size = abs(world_bounds[2] - world_bounds[0]) / 100
    x_range = xmax - xmin
    y_range = ymax - ymin
    mp = (xmin + xmax) / 2, (ymin + ymax) / 2

    if x_range > y_range:
        diff = x_range - y_range
        ymin -= diff / 2
        ymax += diff / 2
    else:
        diff = y_range - x_range
        xmin -= diff / 2
        xmax += diff / 2

    factor = 5
    scaled_square = scale_square(mp, xmin, ymin, xmax, ymax, factor)
    small_enough = scaled_square[0] > world_bounds[0] and scaled_square[2] < world_bounds[2] and scaled_square[1] > world_bounds[1] and scaled_square[3] < world_bounds[3]
    large_enough = scaled_square[2] - scaled_square[0] > min_size and scaled_square[3] - scaled_square[1] > min_size
    while not small_enough:
        factor *= 0.9
        scaled_square = scale_square(mp, xmin, ymin, xmax, ymax, factor)
        small_enough = scaled_square[0] > world_bounds[0] and scaled_square[2] < world_bounds[2] and scaled_square[1] > world_bounds[1] and scaled_square[3] < world_bounds[3]
    while not large_enough:
        factor *= 1.1
        scaled_square = scale_square(mp, xmin, ymin, xmax, ymax, factor)
        large_enough = scaled_square[2] - scaled_square[0] > min_size and scaled_square[3] - scaled_square[1] > min_size
    return scaled_square


def get_russia_bounds(xmin, ymin, xmax, ymax):
    xmax *= 2.75
    xmin *= -0.1
    ymin = ymax - (xmax - xmin)
    return xmin, ymin, xmax, ymax


def get_france_bounds(xmin, ymin, xmax, ymax):
    xmin *= 0.15
    xmax *= 0.2
    ymax *= 0.48
    ymin = ymax - (xmax - xmin)
    return xmin, ymin, xmax, ymax


def get_norway_bounds(xmin, ymin, xmax, ymax):
    xmin *= 0.3
    xmax *= 0.45
    ymax *= 0.77
    ymin = ymax - (xmax - xmin)
    return xmin, ymin, xmax, ymax


def get_netherlands_bounds(xmin, ymin, xmax, ymax):
    xmin *= 0.1
    xmax *= 0.3
    ymax *= 0.5
    ymin = ymax - (xmax - xmin)
    return xmin, ymin, xmax, ymax


def get_liechtenstein_bounds(xmin, ymin, xmax, ymax):
    xmin *= 0.6
    xmax *= 1.3
    ymax *= 1.05
    ymin = ymax - (xmax - xmin)
    return xmin, ymin, xmax, ymax


def get_rwanda_bounds(xmin, ymin, xmax, ymax):
    xmin *= 0.6
    xmax *= 1.3
    ymax *= 4
    ymin = ymax - (xmax - xmin)
    return xmin, ymin, xmax, ymax


def get_portugal_bounds(xmin, ymin, xmax, ymax):
    xmin *= 0.4
    xmax *= 0.4
    ymax *= 0.65
    ymin = ymax - (xmax - xmin)
    return xmin, ymin, xmax, ymax


def get_fiji_bounds(xmin, ymin, xmax, ymax):
    xmax *= 1.13
    xmin *= -0.99
    ymax *= -0.05
    ymin = ymax - (xmax - xmin)
    return xmin, ymin, xmax, ymax


def get_newzealand_bounds(xmin, ymin, xmax, ymax):
    xmax *= 1.2
    xmin *= -0.85
    ymax *= -0.1
    ymin = ymax - (xmax - xmin)
    return xmin, ymin, xmax, ymax


def get_seychell_bounds(xmin, ymin, xmax, ymax):
    xmax *= 0.74
    xmin *= 2.09
    ymax *= -0.18
    ymin = ymax - (xmax - xmin)
    return xmin, ymin, xmax, ymax


path = "country_outlines/countries.geojson"

df = gpd.read_file(path)
df.to_crs("EPSG:3857", inplace=True)
world_bounds = df.total_bounds
color_dark = np.array([240, 141, 0]) / 255.0
color_bright = np.array([255, 225, 150]) / 255.0

id = 47
for i in range(id, id + 1):
    # for i in range(df.shape[0]):
    ctry_names = df["name"]
    ctry_ids = df["ISO3166-1-Alpha-2"]

    df["color"] = [color_dark if country == ctry_names[i] else color_bright for country in ctry_names]
    ax = df.plot(color=df["color"])

    ctry = df.loc[[i], "geometry"]
    xmin, ymin, xmax, ymax = get_minimal_square(*ctry.total_bounds, world_bounds)
    # xmin, ymin, xmax, ymax = ctry.total_bounds
    xmin, ymin, xmax, ymax = get_russia_bounds(xmin, ymin, xmax, ymax)

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    # plt.show()
    ax.set_axis_off()
    plt.savefig(f"country_outlines/imgs/{ctry_ids[i].lower()}_{ctry_names[i]}_{i}.png", dpi=300, bbox_inches="tight", pad_inches=0)
    plt.close()
