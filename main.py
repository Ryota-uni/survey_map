from pathlib import Path
import json

import geopandas as gpd
import plotly.express as px


def main() -> None:
    geojson_path = Path("data/raw/Western.geojson")
    gdf = gpd.read_file(geojson_path, engine="pyogrio")

    # 念のため WGS84 に統一
    if gdf.crs is not None and gdf.crs.to_string() != "EPSG:4326":
        gdf = gdf.to_crs(epsg=4326)

    # Plotly用にID列を付与
    gdf = gdf.reset_index().rename(columns={"index": "feature_id"})

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
        color="survey",
        hover_name="Camp",
        hover_data={
            "District": True,
            "Block": True,
            "Province": True,
            "feature_id": False,
        },
        center={"lat": center_lat, "lon": center_lon},
        zoom=7,
        mapbox_style="open-street-map",
        opacity=0.5,
    )

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    output_path = Path("docs/western_map.html")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(output_path)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()