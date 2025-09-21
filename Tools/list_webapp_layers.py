"""
ArcGIS Web Application Layer Inspector Tool

This tool recursively analyzes ArcGIS web applications (Dashboards, Web Apps, 
Story Maps, Web Experiences) to extract and display all embedded web maps and 
their operational layers. It traverses nested applications and provides 
detailed layer information including names, URLs, and item IDs.

Key Features:
- Supports multiple app types: Dashboard, Web Mapping Application, Story Map, Web Experience
- Recursive processing to handle nested applications
- Extracts web map IDs from various app configurations
- Displays layer hierarchy including group layers and sub-layers
- Prevents infinite recursion with visited item tracking
- Provides detailed layer metadata (hosted vs external services)

Usage: Provide an ArcGIS item ID to analyze its layer structure.
"""

from arcgis.gis import GIS
from arcgis.mapping import WebMap
import arcpy
import re

def extract_webmap_ids(app_type, app_data, item_id, gis):
    """
    Extracts web map IDs from different types of ArcGIS applications.

    Args:
        app_type (str): Type of the application (Dashboard, Web Mapping Application, etc.)
        app_data (dict): JSON data of the application
        item_id (str): ID of the application item
        gis (GIS): GIS connection object

    Returns:
        list: List of unique web map IDs found in the application
    """
    webmap_ids = []
    if app_type in ["Dashboard", "Web Mapping Application", "Story Map"]:
        if "widgets" in app_data:
            for widget in app_data["widgets"]:
                if isinstance(widget, dict):
                    if widget.get("type") == "mapWidget" and "itemId" in widget:
                        webmap_ids.append(widget["itemId"])
                    elif "map" in widget and isinstance(widget["map"], dict) and "itemId" in widget["map"]:
                        webmap_ids.append(widget["map"]["itemId"])
        if "values" in app_data:
            webmap_ids += [
                v.get("itemId") for v in app_data["values"].values()
                if isinstance(v, dict) and "itemId" in v
            ]
        if "operationalLayers" in app_data:
            webmap_ids += [
                l.get("itemId") for l in app_data["operationalLayers"]
                if isinstance(l, dict) and "itemId" in l
            ]
        if "map" in app_data and isinstance(app_data["map"], dict):
            if "itemId" in app_data["map"]:
                webmap_ids.append(app_data["map"]["itemId"])
    elif app_type == "Web Experience":
        if "dataSources" in app_data:
            webmap_ids += [
                ds.get("itemId") for ds in app_data["dataSources"].values()
                if isinstance(ds, dict) and ds.get("type") == "WEB_MAP" and "itemId" in ds
            ]
        exp = WebExperience(item_id, gis=gis)
        for ds in exp.datasources.values():
            if ds.get("type") == "WEB_MAP" and "itemId" in ds:
                webmap_ids.append(ds["itemId"])
    return list(set(filter(None, webmap_ids)))

def display_webmap_layers(webmap_id, gis):
    """
    Displays information about layers in a web map.

    Args:
        webmap_id (str): ID of the web map
        gis (GIS): GIS connection object
    """
    webmap_item = gis.content.get(webmap_id)
    if not webmap_item:
        arcpy.AddWarning(f"Web map with ID {webmap_id} not found.")
        return

    web_map = WebMap(webmap_item)

    for layer in web_map._webmapdict.get('operationalLayers', []):
        name = layer.get("title", "Unknown")
        url = layer.get("url", "No URL")
        item_id = layer.get("itemId", "No ItemId")

        # Check if the layer is a group layer
        if 'layers' in layer:
            arcpy.AddMessage(f"\nGroup Layer: {name}")
            arcpy.AddMessage("-" * 50)
            for sub_layer in layer['layers']:
                sub_name = sub_layer.get("title", "Unknown")
                sub_url = sub_layer.get("url", "No URL")
                sub_item_id = sub_layer.get("itemId", "No ItemId")
                arcpy.AddMessage(f"  Sub Layer Name: {sub_name} | ItemId: {sub_item_id}")
                arcpy.AddMessage(f"  Sub Layer URL: {sub_url}\n")
            arcpy.AddMessage("-" * 50)
        else:
            arcpy.AddMessage(f"\nLayer Name: {name}")
            if "/hosted/wrl" in url.lower():
                arcpy.AddMessage("  (Hosted Layer)")
            else:
                arcpy.AddMessage(f"  ItemId: {item_id}")
            arcpy.AddMessage(f"  Layer URL: {url}\n")
    arcpy.AddMessage("=" * 70)

def process_webexperience_and_list_webapp(item_id, gis):
    """
    Processes a Web Experience item and identifies embedded applications and web maps.

    Args:
        item_id (str): ID of the Web Experience item
        gis (GIS): GIS connection object
    """
    embedded_app_ids = set()

    # Regular expression to find URLs
    url_pattern = re.compile(r'https?://[^\s]+')
    # Regular expression to extract IDs either from query parameters or path segments
    id_pattern = re.compile(r'(?:id=|dashboards/|webappviewer/)([a-zA-Z0-9]+)')
    # Get the experience data - using get_data() instead of data attribute
    try:
        exp_item = gis.content.get(item_id)
        exp_data = exp_item.get_data()

        # Function to recursively search for URLs in the data
        def find_urls(data):
            if isinstance(data, dict):
                for key, value in data.items():
                    find_urls(value)
            elif isinstance(data, list):
                for item in data:
                    find_urls(item)
            elif isinstance(data, str):
                for match in url_pattern.findall(data):
                    for id_match in id_pattern.finditer(match):
                        if len(id_match.group(1)) > 10:
                            embedded_app_ids.add(id_match.group(1))

        # Search for URLs in the experience data
        find_urls(exp_data)
    except Exception as e:
        arcpy.AddWarning(f"Error processing experience data: {str(e)}")
    arcpy.AddMessage(f"Found {len(embedded_app_ids)} webapp(s) nested in experience builder\nApp IDs: {embedded_app_ids}")
    for app_id in embedded_app_ids:
        process_any_item(app_id, gis)

def process_any_item(item_id, gis, visited=None):
    """
    Processes any ArcGIS item and recursively processes related items.

    Args:
        item_id (str): ID of the item to process
        gis (GIS): GIS connection object
        visited (set, optional): Set of already visited item IDs to prevent infinite recursion
    """
    if visited is None:
        visited = set()
    if item_id in visited:
        return
    visited.add(item_id)
    item = gis.content.get(item_id)
    if not item:
        arcpy.AddWarning(f"Item ID {item_id} not found. Check if you are connected to the correct ArcGIS server (AGOL or PORTAL)")
        return
    arcpy.AddMessage("#" * 70)
    arcpy.AddMessage(f"Processing {item.type}: {item.title}")
    arcpy.AddMessage(f"with ID: {item_id}")
    if item.type == "Web Map":
        display_webmap_layers(item_id, gis)
    elif item.type == "Web Experience":
        process_webexperience_and_list_webapp(item_id, gis)
    elif item.type in ["Dashboard", "Web Mapping Application", "Story Map"]:
        app_data = item.get_data()
        webmap_ids = extract_webmap_ids(item.type, app_data, item_id, gis)
        for wm_id in webmap_ids:
            process_any_item(wm_id, gis, visited)
    else:
        arcpy.AddWarning(f"Unhandled item type: {item.type}")

def report_invalid_item():
    """
    Reports an error when an invalid item ID is provided.
    """
    arcpy.AddError("Provided URL does not point to a valid item. Please check if the ItemID is correct and if the active portal is set correctly (AGOL or MSF PORTAL).")

def log_section(title):
    """
    Logs a section header with the given title.

    Args:
        title (str): Title of the section
    """
    arcpy.AddMessage("_" * 25 + "GIS Center Gremlins message" + "_" * 25)
    arcpy.AddMessage(title)
    arcpy.AddMessage("_" * 70)

if __name__ == "__main__":
    """
    Main execution block for processing a web app item ID provided by the user.
    Establishes a connection to the current ArcGIS Pro session and processes the item.
    """
    # Establish a connection to the current ArcGIS Pro session.
    gis = GIS("pro")

    # Retrieve the item ID from the user's input parameter.
    item_id = arcpy.GetParameterAsText(0).strip()  # Input web app item_id from the user

    # Process the item with the given ID.
    process_any_item(item_id, gis)
