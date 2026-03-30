from pathlib import Path
import json

import geopandas as gpd
import plotly.express as px
import pandas as pd


def main() -> None:
    geojson_path = Path("data/raw/Western.geojson")
    gdf = gpd.read_file(geojson_path, engine="pyogrio")

    # 念のため WGS84 に統一
    if gdf.crs is not None and gdf.crs.to_string() != "EPSG:4326":
        gdf = gdf.to_crs(epsg=4326)

    # Plotly用にID列を付与
    gdf = gdf.reset_index().rename(columns={"index": "feature_id"})

    # 表示対象の条件
    target_districts = ["Mongu", "Nalolo", "Limulunga"]

    gdf["map_group"] = "Other"
    mask = (gdf["survey"] == 1) & (gdf["District"].isin(target_districts))
    gdf.loc[mask, "map_group"] = "Survey area"

    # GeoJSON化
    geojson_data = json.loads(gdf.to_json())

    # 地図中心を計算
    bounds = gdf.total_bounds
    center_lon = (bounds[0] + bounds[2]) / 2
    center_lat = (bounds[1] + bounds[3]) / 2

    fig = px.choropleth_mapbox(
        gdf,
        geojson=geojson_data,
        locations="feature_id",
        featureidkey="properties.feature_id",
        color="map_group",
        color_discrete_map={
            "Survey area": "#d95f0e",
            "Other": "#d9d9d9",
        },
        hover_name="Camp",
        hover_data={
            "District": True,
            "Block": True,
            "Province": True,
            "survey": True,
            "map_group": False,
            "feature_id": False,
        },
        center={"lat": center_lat, "lon": center_lon},
        zoom=7,
        mapbox_style="open-street-map",
        opacity=0.6,
    )

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        legend_title_text="Area type",
    )

    docs_dir = Path("docs")
    docs_dir.mkdir(parents=True, exist_ok=True)

    map_path = docs_dir / "western_map.html"
    fig.write_html(map_path, include_plotlyjs="cdn")
    print(f"Saved: {map_path}")



if __name__ == "__main__":
    main()