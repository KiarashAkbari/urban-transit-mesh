import folium

def generate_urban_mesh_map():
    # Center around the geometric center of Iran
    map_center = [32.4279, 53.6880]
    
    # Create base map zoomed out to show the whole country
    mesh_map = folium.Map(location=map_center, zoom_start=5, tiles="CartoDB positron")


    # Mock Data: "Traffic incidents" or "Infrastructure maintenance" (Red Zones)
    restricted_zones = [
        [[35.7000, 51.4000], [35.7100, 51.4000], [35.7100, 51.4100], [35.7000, 51.4100]],
        [[35.6500, 51.3500], [35.6600, 51.3500], [35.6600, 51.3700], [35.6500, 51.3700]]
    ]

    # Mock Data: "Clear transit hubs" or "Safe assembly points" (Green Zones)
    clear_hubs = [
        [35.7200, 51.3300],
        [35.6800, 51.4200]
    ]

    # Plot Restricted Zones (Red Polygons)
    for zone in restricted_zones:
        folium.Polygon(
            locations=zone,
            color='red',
            fill=True,
            fill_color='red',
            fill_opacity=0.4,
            tooltip='Restricted Transit Area'
        ).add_to(mesh_map)

    # Plot Clear Hubs (Green Markers)
    for hub in clear_hubs:
        folium.CircleMarker(
            location=hub,
            radius=8,
            color='green',
            fill=True,
            fill_color='green',
            fill_opacity=0.7,
            tooltip='Clear Transit Hub'
        ).add_to(mesh_map)

    # Save the initial HTML file
    output_filename = "mesh_map_base.html"
    mesh_map.save(output_filename)
    print(f"Generated base map: {output_filename}")

if __name__ == "__main__":
    generate_urban_mesh_map()
