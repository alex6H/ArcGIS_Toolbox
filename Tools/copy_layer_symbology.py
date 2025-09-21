"""
Tool Name: Web Map Layer Synchronizer Tool

Summary: This tool synchronizes layer settings from a source web map to one or more target web maps.
It finds layers with matching names and data sources, then copies visual and functional settings.

Parameters:
    Source Web Map ID: The Item ID of the source web map to copy settings from
    Target Web Map IDs: Semicolon-separated list of target web map IDs
    Layer Names: Semicolon-separated list of layer names to synchronize
    Copy Display Settings: Boolean to copy visibility, opacity, and scale settings
    Copy Popup Settings: Boolean to copy popup configuration
    Copy Symbology Effects: Boolean to copy renderer and visual effects
    Verbose Output: Boolean to enable detailed logging

Key Features:
    - Synchronizes layer settings between multiple web maps
    - Preserves group layer structures
    - Matches layers by name and data source
    - Copies display, popup, and symbology settings
    - Handles nested group layers
    - Provides detailed progress reporting

Usage: For maintaining consistent layer appearance across multiple web maps.

Requirements:
    - ArcGIS Pro with portal connection
    - Valid ArcGIS Online credentials
    - Edit permissions on target web maps

Returns: True if successful; False otherwise.

Date: April 2025
File: copy_layer_symbology.py
Author: github.com/alex6H
"""

import arcpy
import json
from arcgis.gis import GIS
from arcgis.mapping import WebMap
import re
	
        
def get_webmap(gis, webmap_id):
    """Retrieve a webmap by its ID"""
    try:
        item = gis.content.get(webmap_id)
        if item and item.type == "Web Map":
            webmap = WebMap(item)
            return webmap, item
        else:
            arcpy.AddWarning(f"Item {webmap_id} is not a valid Web Map")

            return None, None
    except Exception as e:
        error_msg = f"Error retrieving web map {webmap_id}: {str(e)}"
        arcpy.AddWarning(error_msg)

        return None, None

def get_all_layers(layer_list, result=None):
    """Recursively get all layers including those in groups"""
    if result is None:
        result = []
    
    for layer in layer_list:
        result.append(layer)
        # Check if this is a group layer
        if 'layers' in layer:
            get_all_layers(layer.layers, result)
    
    return result

def get_layer_data_source(layer):
    """Extract data source information from a layer"""
    try:
        # Different layer types may store source information differently
        if 'url' in layer:
            return layer.url
        elif 'serviceItemId' in layer:
            return layer.serviceItemId
        else:
            return None
    except:
        return None

def is_layer_match(source_layer, target_layer, layer_names):
    """Check if layers match by name and data source"""
    # First check if layer name is in our list to sync
    if source_layer.title not in layer_names:
        return False
    
    # Then check if target layer name matches source layer name
    if source_layer.title != target_layer.title:
        return False
    
    # Finally check if data sources match
    source_data = get_layer_data_source(source_layer)
    target_data = get_layer_data_source(target_layer)
    
    if source_data and target_data and source_data == target_data:
        return True
    
    return False

def copy_layer_settings(source_layer, target_layer,
                        copy_display, copy_popup, copy_symbology) -> list:
    properties_copied = []

    # Copy basic display settings
    if copy_display:
        for prop in ['opacity', 'visibility', 'definitionExpression', 'showLabels', 'disablePopup', 'showLegend']:
            if hasattr(source_layer, prop):
                setattr(target_layer, prop, getattr(source_layer, prop))
                properties_copied.append(prop)

        if hasattr(source_layer, 'layerDefinition') and hasattr(target_layer, 'layerDefinition'):
            s_def = source_layer.layerDefinition
            t_def = target_layer.layerDefinition
            for prop in ['minScale', 'maxScale', 'featureReduction']:
                if prop in s_def:
                    t_def[prop] = s_def[prop]
                    properties_copied.append(prop)
            target_layer.layerDefinition = t_def

    # Copy drawingInfo
    if copy_display and hasattr(source_layer.layerDefinition, 'drawingInfo'):
        target_layer.layerDefinition['drawingInfo'] = source_layer.layerDefinition['drawingInfo']
        properties_copied.append('drawingInfo')

    # Copy popupInfo
    if copy_popup and hasattr(source_layer, 'popupInfo'):
        target_layer.popupInfo = source_layer.popupInfo
        properties_copied.append('popupInfo')

    # Copy symbology and visual effects
    if copy_symbology:
        if hasattr(source_layer, 'layerDefinition') and hasattr(target_layer, 'layerDefinition'):
            s_def = source_layer.layerDefinition
            t_def = target_layer.layerDefinition
            for prop in ['featureReduction', 'featureEffect']:
                if prop in s_def:
                    t_def[prop] = s_def[prop]
                    properties_copied.append(prop)
            if 'drawingInfo' in s_def:
                t_def['drawingInfo'] = s_def['drawingInfo']
                properties_copied.append('drawingInfo')
            target_layer.layerDefinition = t_def

    return properties_copied

def sync_webmaps(source_webmap_id, target_ids, layer_names,
                 copy_display, copy_popup, copy_symbology,
                 verbose):


    """Main function to synchronize layers between webmaps"""
    try:
        # Initialize gis variable
        gis = None
        # Connect to portal
        try:
            arcpy.AddMessage("Connecting to portal...")
            # Attempt to connect using the ArcGIS Pro active portal
            gis = GIS("pro")
            arcpy.AddMessage(f"Connected as: {gis.users.me.username}")
        except Exception as e:
            # Log error if connection fails
            error_msg = f"Failed to connect to portal: {str(e)}"
            arcpy.AddError(error_msg)
            # No need to return here, the check below will handle it

        # Check if the GIS connection was successful
        if not gis:
            # Add a specific error message if connection failed and exit
            arcpy.AddError("Could not establish connection to Portal/AGOL. Exiting.")
            return False

        # --- Get source webmap ---
        # Use try-except block to handle potential errors from get_webmap
        # (e.g., map not found, not a webmap), similar to agol_copy_webmap_layer.py
        try:
            source_webmap, source_item = get_webmap(gis, source_webmap_id)
            # Log successful loading of the source webmap
            arcpy.AddMessage(f"Successfully loaded source web map: '{source_item.title}' (ID: {source_webmap_id})")
        except ValueError as ve:
            # Log specific error from get_webmap (e.g., not found, wrong type)
            arcpy.AddError(f"Failed to load source webmap (ID: {source_webmap_id}): {str(ve)}")
            return False # Exit if source map cannot be loaded
        except Exception as e:
            # Log any other unexpected error during source webmap retrieval
            arcpy.AddError(f"An unexpected error occurred while loading source webmap (ID: {source_webmap_id}): {str(e)}")
            return False # Exit on unexpected error

        # Get all layers from source webmap including those in groups
        # Use the recursive get_all_layers function
        source_layers_all = get_all_layers(source_webmap.layers)
        arcpy.AddMessage(f"Found {len(source_layers_all)} layers in source web map '{source_item.title}'")

        # If verbose, dump the JSON/dict structure of source layers
        if verbose:
            arcpy.AddMessage("Verbose Mode Enabled: Dumping Source Layer Dictionaries...")
            for layer in source_layers_all:
                try:
                    layer_dict = layer.to_dict() if hasattr(layer, 'to_dict') else dict(layer)
                    arcpy.AddMessage(json.dumps(layer_dict, indent=2))
                except Exception as ve:
                    arcpy.AddWarning(f"Could not serialize layer: {getattr(layer, 'title', 'Unnamed')} - {str(ve)}")

        # Initialize counter for total updates made
        total_updates = 0

        # --- Process each target webmap ID provided ---
        for target_id in target_ids:
            # Skip if the target ID is empty or whitespace
            if not target_id:
                arcpy.AddWarning("Skipping empty target web map ID.")
                continue

            # --- Retrieve the target webmap using its ID ---
            # Use try-except block for target webmap retrieval
            try:
                target_webmap, target_item = get_webmap(gis, target_id)
                # Log which target webmap is being processed
                arcpy.AddMessage(f"\nProcessing target web map: '{target_item.title}' (ID: {target_id})")
            except ValueError as ve:
                # Log specific error from get_webmap and skip this target
                arcpy.AddWarning(f"Skipping target webmap (ID: {target_id}): {str(ve)}")
                continue # Move to the next target ID
            except Exception as e:
                # Log unexpected error and skip this target
                arcpy.AddWarning(f"Skipping target webmap (ID: {target_id}) due to unexpected error: {str(e)}")
                continue # Move to the next target ID

            # Get all layers from the current target webmap
            target_layers_all = get_all_layers(target_webmap.layers)
            arcpy.AddMessage(f" Found {len(target_layers_all)} layers in target web map '{target_item.title}'")

            # Track if any updates were made to this specific webmap
            webmap_updated = False

            # Iterate through source layers to find matches in the target webmap
            for source_layer in source_layers_all:
                # Iterate through target layers to find a match for the current source layer
                for target_layer in target_layers_all:
                    # Check if the source and target layers match based on name and data source
                    if is_layer_match(source_layer, target_layer, layer_names):
                        # If layers match, copy settings from source to target
                        properties = copy_layer_settings(source_layer, target_layer,
                                 copy_display, copy_popup, copy_symbology)

                        # Check if any properties were successfully copied
                        if properties:
                            # Mark the webmap as updated
                            webmap_updated = True
                            # Increment the total update counter
                            total_updates += 1
                            # Format the list of copied properties for logging
                            props_str = ", ".join(properties)
                            # Log the specific update made
                            msg = f"Updated layer '{target_layer.title}' in '{target_item.title}': Copied {props_str}"
                            arcpy.AddMessage(f"  - {msg}")
                        # Assuming only one target layer matches a source layer, break inner loop once match found and processed
                        # If multiple target layers could potentially match (e.g. same layer added twice), remove this break
                        break

            # Save the target webmap if any settings were updated
            if webmap_updated:
                try:
                    # Attempt to save the changes to the webmap on the portal
                    target_webmap.update()
                    arcpy.AddMessage(f"Successfully updated and saved web map: '{target_item.title}'")
                except Exception as save_error:
                    # Log an error if saving the webmap fails
                    error_msg = f"Failed to save web map '{target_item.title}': {str(save_error)}"
                    arcpy.AddError(error_msg) # Use AddError as saving failure is significant
            else:
                # Log if no matching layers were found or updated in the target webmap
                arcpy.AddMessage(f"No matching layers found or updated in: '{target_item.title}'")

        # Log the completion of the process and the total number of layer updates
        arcpy.AddMessage(f"\nProcess complete. Total layer updates across all target web maps: {total_updates}")
        return True

    # Catch any unexpected exceptions during the main sync process
    except Exception as e:

        error_msg = f"An unexpected error occurred during webmap synchronization: {str(e)}"
        arcpy.AddError(error_msg)
        return False
    
def extract_item_id_from_title(webmap_input):
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

def main():
    """Main function that handles the tool parameters and execution"""
    try:
        # Get source webmap and extract item ID
        source_webmap_input = arcpy.GetParameterAsText(0)
        source_webmap = extract_item_id_from_title(source_webmap_input)  # Extract item ID using the function

        # Get target webmap as a semicolon-separated string and extract item IDs
        raw_target_webmaps = arcpy.GetParameterAsText(1).split(";")
        
        # Clean up the list: remove empty, None, or whitespace-only entries and extract item IDs
        target_ids = [
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

        # Parameter 3: Copy Display Settings (Visibility, Opacity, Scale)
        copy_display_settings = arcpy.GetParameter(3)

        # Parameter 4: Copy Popup Settings (popupInfo + disablePopup)
        copy_popup_settings = arcpy.GetParameter(4)

        # Parameter 5: Copy Symbology and Effects (Renderer, Labeling, FeatureEffect, FeatureReduction)
        copy_symbology_effects = arcpy.GetParameter(5)

        # Parameter 6: Verbose output
        verbose = arcpy.GetParameter(6)

        # Log the parameters being used for the operation
        arcpy.AddMessage("--- Script Parameters ---")
        arcpy.AddMessage(f"Source Web Map ID: {source_webmap}")
        arcpy.AddMessage(f"Target Web Map IDs: {', '.join(target_ids)}")
        arcpy.AddMessage(f"Layers to synchronize: {', '.join(layer_names)}")
        arcpy.AddMessage("-------------------------")


        # Check if essential parameters are provided
        if not source_webmap:
            arcpy.AddError("Source Web Map ID is required.")
            return # Exit if source ID is missing
        if not target_ids:
            arcpy.AddError("At least one Target Web Map ID is required.")
            return # Exit if target IDs are missing
        if not layer_names:
            arcpy.AddError("At least one Layer Name is required.")
            return # Exit if layer names are missing

        # Call the main synchronization function with the processed parameters
        success = sync_webmaps(
                    source_webmap, target_ids, layer_names,
                    copy_display_settings, copy_popup_settings, copy_symbology_effects,
                    verbose
                )

        # Optionally, add a final status message based on the return value
        if success:
            arcpy.AddMessage("\nSynchronization process finished successfully.")
        else:
            arcpy.AddError("\nSynchronization process finished with errors.")


    # Catch any unexpected exceptions during parameter processing or function call
    except Exception as e:
        error_msg = f"An unexpected error occurred in the main execution block: {str(e)}"
        arcpy.AddError(error_msg)


# Standard Python entry point check
if __name__ == "__main__":
   
    main()