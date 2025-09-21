"""
Tool Name: Copy Layers Between Web Maps

Summary: Copies layers from a source Web Map to target Web Maps in ArcGIS Online, preserving group structures and resolving name conflicts.

Parameters:
    source_webmap_input (str): Source web map in 'Title [ItemID]' format.
    raw_target_webmaps (str): Semicolon-delimited target web maps in 'Title [ItemID]' format.
    raw_layer_names (str): Semicolon-delimited list of layer titles to copy.

Key Functionalities:
    - Extracts item IDs using regex.
    - Logs tool runs with timestamp and user email.
    - Verifies user permissions for editing.
    - Avoids duplicate layers by checking existing titles.
    - Handles nested group layers.
    - Resolves name conflicts with numeric suffixes.
    - Outputs messages to ArcGIS Pro’s Geoprocessing pane.

Usage: For managing cartographic products across multiple Web Maps.

Requirements:
    - ArcGIS Pro with portal connection
    - Valid ArcGIS Online credentials

Returns: True if successful; raises exceptions otherwise.

Date: April 2025
File : copy_layer_between_webmap.py
Author: github.com/alex6H
"""


# Standard library imports
import json
import copy
import re
from typing import List, Tuple, Optional, Dict, Any

# Third-party imports  
from arcgis.gis import GIS
from arcgis.mapping import WebMap

# ArcGIS imports
import arcpy

def extract_item_id(webmap_input: str) -> str:
    return webmap_input

def get_webmap(gis: GIS, webmap_input: str) -> Tuple[WebMap, Any]:
    item_id = extract_item_id(webmap_input)
    item = gis.content.get(item_id)
    if not item:
        raise ValueError(f"WebMap with ID {item_id} not found")
    if item.type != "Web Map":
        raise ValueError(f"Item {item_id} is not a Web Map")
    arcpy.AddMessage(f"Found WebMap: '{item.title}' (Owner: {item.owner})")
    return WebMap(item), item

def find_layer_by_name(webmap: WebMap, layer_name: str) -> Dict[str, Any]:
    """
    Finds a layer or group layer configuration by its title in the webmap definition.
    Prioritizes returning a GroupLayer if its title matches the layer_name at a given level.
    Performs a depth-first search.
    """
    webmap_data = webmap.definition
    def search_layers(layers: List[Dict[str, Any]], target_name: str) -> Optional[Dict[str, Any]]:
        # First pass: Check for exact title match at the current level.
        # Prioritize finding a GroupLayer.
        found_layer = None
        found_group = None
        for layer in layers:
            if layer.get('title') == target_name:
                if layer.get('layerType') == 'GroupLayer':
                    arcpy.AddMessage(f"Found matching Group Layer: '{target_name}'. Prioritizing this.")
                    found_group = layer
                    break # Found the prioritized group, stop searching this level for matches
                elif found_layer is None: # Found a non-group match, store it but keep looking for a group at this level
                     arcpy.AddMessage(f"Found matching layer (non-group): '{target_name}'. Continuing search at this level for potential group layer match.")
                     found_layer = layer

        if found_group:
            return found_group # Return prioritized group config
        if found_layer:
             arcpy.AddMessage(f"Returning non-group layer: '{target_name}' as no matching group layer was found at this level.")
             return found_layer # Return the first non-group match if no group matched at this level

        # Second pass: Recurse into group layers if no direct match found at this level
        for layer in layers:
            if layer.get('layerType') == 'GroupLayer' and 'layers' in layer:
                 # Search within this group
                 sub_match = search_layers(layer.get('layers', []), target_name)
                 if sub_match:
                     # Found something inside the group (could be layer or nested group)
                     return sub_match # Return the config found within

        return None # Not found at this level or below

    layer_config = search_layers(webmap_data.get('operationalLayers', []), layer_name)
    if layer_config:
        return layer_config
    # Update error message slightly for clarity
    raise ValueError(f"Layer or Group Layer '{layer_name}' not found in source web map")

def find_in_group(layers: List[Dict[str, Any]], target_name: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Recursively searches within GroupLayers in the provided list `layers`
    to find if a layer or nested group with `target_name` exists as a child.
    Returns (True, immediate_parent_group_config) if found, otherwise (False, None).
    """
    for layer in layers:
        # Check only within GroupLayers
        if layer.get('layerType') == 'GroupLayer' and 'layers' in layer:
            # Check direct children of this group
            for sublayer in layer.get('layers', []):
                if sublayer.get('title') == target_name:
                    arcpy.AddMessage(f"Target '{target_name}' found as a direct sublayer of group '{layer.get('title')}'")
                    # Return True and the config of the immediate parent group
                    return True, layer

            # If not a direct child, recurse into nested groups within this group
            # Pass the children of the current group to the recursive call
            found, parent = find_in_group(layer.get('layers', []), target_name)
            if found:
                # If found deeper, return the result from that deeper call.
                # The 'parent' returned will be the immediate parent from that deeper level.
                return True, parent

    # Target name was not found within any group layer in the provided list 'layers'
    return False, None

def copy_layer_between_webmaps(gis: GIS, source_webmap: str, target_webmap: str, layer_names: List[str]) -> bool:
    source_wm, source_item = get_webmap(gis, source_webmap)
    target_wm, target_item = get_webmap(gis, target_webmap)
    current_user = gis.properties.user.username

    has_edit_rights = (target_item.owner == current_user) or gis.users.me.role in ('org_admin', 'account_admin')
    if not has_edit_rights:
        raise PermissionError("You don't have permission to edit the target web map")
    
    source_definition = source_wm.definition
    target_definition = target_wm.definition
    
    for layer_name in layer_names:
        layer_config = find_layer_by_name(source_wm, layer_name)
        is_group_layer, parent_layer = find_in_group(source_definition.get('operationalLayers', []), layer_name)
        
        if is_group_layer and parent_layer:
            group_name = parent_layer.get('title')
            arcpy.AddMessage(f"Layer '{layer_name}' is part of group '{group_name}'")
            
            # Check if group exists
            group_exists = False
            for i, layer in enumerate(target_definition.get('operationalLayers', [])):
                if layer.get('title') == group_name and layer.get('layerType') == 'GroupLayer':
                    group_exists = True
                    arcpy.AddMessage(f"Found existing group '{group_name}' in target map")
                    
                    # Check if layer with same name exists in group
                    layer_exists = False
                    for j, sublayer in enumerate(layer.get('layers', [])):
                        if sublayer.get('title') == layer_name:
                            layer_exists = True
                            arcpy.AddMessage(f"Layer '{layer_name}' already exists in group '{group_name}'. Skipping...")
                            break
                    
                    if not layer_exists:
                        # Only add the layer if it doesn't already exist in the group
                        arcpy.AddMessage(f"Adding layer '{layer_name}' to existing group '{group_name}'")
                        layer.get('layers').append(copy.deepcopy(layer_config))
                    break
            
            if not group_exists:
                arcpy.AddMessage(f"Creating a new group '{group_name}' with layer '{layer_name}'")
                # Create a new group with just the specific layer
                new_group = {
                    'title': group_name,
                    'layerType': 'GroupLayer',
                    'visibility': True,
                    'layers': [copy.deepcopy(layer_config)]
                }
                target_definition['operationalLayers'].append(new_group)

        else:
            # Check if layer with same name exists at root level
            layer_exists = False
            existing_layer_names = [layer.get('title') for layer in target_definition.get('operationalLayers', [])]
            
            if layer_name in existing_layer_names:
                layer_exists = True
                # Generate a unique name with incremental suffix
                new_layer_name = generate_unique_name(layer_name, existing_layer_names)
                arcpy.AddWarning(f"Layer '{layer_name}' already exists in target web map. Adding as '{new_layer_name}'")
                
                # Copy the layer config and update the title
                new_layer_config = copy.deepcopy(layer_config)
                new_layer_config['title'] = new_layer_name
                target_definition['operationalLayers'].append(new_layer_config)
            else:
                arcpy.AddMessage(f"Adding layer '{layer_name}' to target web map")
                target_definition['operationalLayers'].append(layer_config)
    
    definition_dict = dict(target_definition)
    target_item.update({'text': json.dumps(definition_dict)})
    arcpy.AddMessage("Target webmap successfully updated and saved.")
    return True

def generate_unique_name(base_name: str, existing_names: List[str]) -> str:
    """
    Generate a unique name by adding incremental suffix (_1, _2, etc.)
    
    Args:
        base_name (str): The original name
        existing_names (list): List of existing names to check against
    
    Returns:
        str: A unique name that doesn't exist in the list
    """
    if base_name not in existing_names:
        return base_name
    
    counter = 1
    while True:
        new_name = f"{base_name}_{counter}"
        if new_name not in existing_names:
            return new_name
        counter += 1
        
def extract_item_id_from_title(webmap_input: str) -> Optional[str]:
    """
    Extracts the item ID from a string formatted as 'Title [ItemID]'.
    Returns the item ID as a string, or None if not found.
    """
    if not webmap_input:
        return None
   
    # Strip all types of quotes (both single and double)
    cleaned_input = webmap_input.strip().replace('"', '').replace("'", '')
    
    # Use regex to find the item ID within the brackets
    match = re.search(r"\[([a-f0-9]{32})\]$", cleaned_input, re.IGNORECASE)  # Match 32-character item IDs
    
    # Log the found item ID or None if not found
    item_id = match.group(1) if match else None
   
    return item_id

def main() -> None:
    # Get source webmap and extract item ID
    source_webmap_input = arcpy.GetParameterAsText(0)
    source_webmap = extract_item_id_from_title(source_webmap_input)  # Extract item ID using the function

    # Get target webmap as a semicolon-separated string and extract item IDs
    raw_target_webmaps = arcpy.GetParameterAsText(1).split(";")
    
    # Clean up the list: remove empty, None, or whitespace-only entries and extract item IDs
    target_webmaps = [
        item_id_extracted
        for item_id in raw_target_webmaps
        if item_id and item_id.strip()
        for item_id_extracted in [extract_item_id_from_title(item_id)]
        if item_id_extracted is not None
    ]
   
    # Get layer names as a semicolon-separated string
    raw_layer_names = arcpy.GetParameterAsText(2).split(";")
   
    # Clean up the list: remove empty, None, or whitespace-only entries, and strip quotes
    layer_names = [
        name.strip().strip("'\"")
        for name in raw_layer_names
        if name and name.strip()
    ]

    arcpy.AddMessage(f"Source WebMap ID: {source_webmap}")
    arcpy.AddMessage(f"Target WebMap IDs: {', '.join(target_webmaps)}")
    arcpy.AddMessage(f"Layers to copy: {', '.join(layer_names)}")
    
    if not target_webmaps:
        arcpy.AddError("No valid target WebMap IDs provided.")
        return # Exit if no targets specified

    if not layer_names:
        arcpy.AddError("No valid layer names provided.")
        return # Exit if no layers specified

    try:
        gis = GIS("pro")

        # Get portal name or URL for message clarity
        portal_name = gis.properties.get("name", gis._portal.resturl)
        
        # Get current user
        current_user = gis.users.me.username if gis.users.me else "unknown"
        
        arcpy.AddMessage(f"Connected to portal: {portal_name} as user: {current_user}")

        # Loop through each target webmap ID
        processed_count = 0
        error_count = 0
        for target_webmap_id in target_webmaps:
            arcpy.AddMessage(f"\n--- Processing Target WebMap: {target_webmap_id} ---")
            try:
                # Attempt to copy layers to the current target webmap
                success = copy_layer_between_webmaps(gis, source_webmap, target_webmap_id, layer_names)
                if success:
                    arcpy.AddMessage(f"Successfully processed target WebMap: {target_webmap_id}")
                    processed_count += 1
                else:
                    # This case might not happen if copy_layer raises exceptions on failure
                    arcpy.AddWarning(f"Processing target WebMap {target_webmap_id} did not explicitly succeed (check logs).")

            except Exception as e:
                # Log error for this specific target map and continue with the next
                arcpy.AddError(f"Failed to process target WebMap {target_webmap_id}: {str(e)}")
                error_count += 1

        arcpy.AddMessage(f"\n--- Finished processing all target WebMaps ---")
        arcpy.AddMessage(f"Successfully processed: {processed_count} target(s).")
        arcpy.AddMessage(f"Failed to process: {error_count} target(s).")
        if error_count > 0:
             arcpy.AddWarning("One or more target web maps failed to process. Please review the messages above.")


    except Exception as e:
        # Catch broader errors like GIS connection failure or issues before the loop
        arcpy.AddError(f"A critical error occurred: {str(e)}")

if __name__ == "__main__":

    main()
