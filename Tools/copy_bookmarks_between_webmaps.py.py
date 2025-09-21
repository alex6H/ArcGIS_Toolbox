"""
Tool Name: Copy Bookmarks Between Web Maps

Summary: This tool copies all bookmarks from a source web map to one or more target web maps.
It handles duplicate bookmark names by adding incremental suffixes and provides comprehensive
logging for enterprise GIS workflows.

Parameters:
    Source WebMap: The source web map in 'Title [ItemID]' format to copy bookmarks from
    Target WebMaps: Semicolon-separated list of target web maps in 'Title [ItemID]' format
    Verbose Logging: Boolean to enable detailed debugging output

Key Features:
    - Copies all bookmarks from source to multiple target web maps
    - Handles duplicate bookmark names with incremental suffixes (_1, _2, etc.)
    - Preserves bookmark geometry and properties
    - Validates user permissions for target web maps
    - Provides comprehensive progress reporting
    - Supports batch processing of multiple target web maps

Usage: For maintaining consistent spatial bookmarks across multiple web maps.

Requirements:
    - ArcGIS Pro with portal connection
    - Valid ArcGIS Online credentials
    - Edit permissions on target web maps

Returns: Summary statistics of processed web maps and bookmark counts

Date: April 2025
File: copy_bookmarks_between_webmaps.py
Author: github.com/alex6H
"""

import arcpy
import json
import copy
import re
from typing import List, Tuple, Dict, Any, Optional
from arcgis.gis import GIS
from arcgis.mapping import WebMap

def extract_item_id_from_title(webmap_input: str) -> Optional[str]:
    """
    Extracts the item ID from a string formatted as 'Title [ItemID]'.
    
    Args:
        webmap_input (str): Input string in format 'Title [ItemID]'
        
    Returns:
        Optional[str]: The extracted 32-character item ID, or None if not found
        
    Raises:
        None: Returns None for invalid inputs rather than raising exceptions
    """
    if not webmap_input:
        return None
   
    # Strip all types of quotes (both single and double)
    cleaned_input = webmap_input.strip().replace('"', '').replace("'", '')
    
    # Use regex to find the item ID within the brackets
    match = re.search(r"\[([a-f0-9]{32})\]$", cleaned_input, re.IGNORECASE)
    
    # Return the found item ID or None if not found
    item_id = match.group(1) if match else None
   
    return item_id


def get_webmap_and_item(gis: GIS, webmap_id: str, verbose: bool = False) -> Tuple[WebMap, Any]:
    """
    Retrieves a WebMap object and its corresponding item from ArcGIS Online/Portal.
    
    Args:
        gis (GIS): Authenticated GIS connection object
        webmap_id (str): The web map item ID (32-character string)
        verbose (bool): Enable detailed logging for debugging
        
    Returns:
        Tuple[WebMap, Any]: WebMap object and Item object
        
    Raises:
        ValueError: If webmap is not found or is not a valid Web Map type
    """
    if verbose:
        arcpy.AddMessage(f"Attempting to retrieve WebMap with ID: {webmap_id}")
    
    item = gis.content.get(webmap_id)
    if not item:
        raise ValueError(f"WebMap with ID {webmap_id} not found")
    
    if item.type != "Web Map":
        raise ValueError(f"Item {webmap_id} is not a Web Map (Type: {item.type})")
    
    arcpy.AddMessage(f"Found WebMap: '{item.title}' (Owner: {item.owner})")
    
    if verbose:
        arcpy.AddMessage(f"WebMap created: {item.created}, modified: {item.modified}")
    
    return WebMap(item), item


def extract_bookmarks_from_webmap(webmap: WebMap, verbose: bool = False) -> List[Dict[str, Any]]:
    """
    Extracts all bookmarks from a web map definition.
    
    Args:
        webmap (WebMap): The source WebMap object
        verbose (bool): Enable detailed logging for debugging
        
    Returns:
        List[Dict[str, Any]]: List of bookmark configurations
        
    Raises:
        None: Returns empty list if no bookmarks found
    """
    webmap_definition = webmap.definition
    bookmarks = webmap_definition.get('bookmarks', [])
    
    if verbose:
        arcpy.AddMessage(f"Found {len(bookmarks)} bookmark(s) in source webmap")
        for i, bookmark in enumerate(bookmarks):
            bookmark_name = bookmark.get('name', f'Unnamed_{i}')
            arcpy.AddMessage(f"  - Bookmark {i+1}: '{bookmark_name}'")
    
    return bookmarks


def generate_unique_bookmark_name(base_name: str, existing_names: List[str]) -> str:
    """
    Generates a unique bookmark name by adding incremental suffix (_1, _2, etc.).
    
    Args:
        base_name (str): The original bookmark name
        existing_names (List[str]): List of existing bookmark names to check against
        
    Returns:
        str: A unique bookmark name that doesn't exist in the list
    """
    if base_name not in existing_names:
        return base_name
    
    counter = 1
    while True:
        new_name = f"{base_name}_{counter}"
        if new_name not in existing_names:
            return new_name
        counter += 1


def check_edit_permissions(gis: GIS, target_item: Any, verbose: bool = False) -> bool:
    """
    Checks if the current user has edit permissions for the target web map.
    
    Args:
        gis (GIS): Authenticated GIS connection object
        target_item (Any): The target web map item object
        verbose (bool): Enable detailed logging for debugging
        
    Returns:
        bool: True if user has edit permissions, False otherwise
        
    Raises:
        PermissionError: If user lacks edit permissions
    """
    current_user = gis.properties.user.username
    user_role = gis.users.me.role
    
    has_edit_rights = (
        target_item.owner == current_user or 
        user_role in ('org_admin', 'account_admin')
    )
    
    if verbose:
        arcpy.AddMessage(f"Permission check - Current user: {current_user}, Role: {user_role}")
        arcpy.AddMessage(f"Target item owner: {target_item.owner}")
        arcpy.AddMessage(f"Edit rights granted: {has_edit_rights}")
    
    if not has_edit_rights:
        raise PermissionError(
            f"You don't have permission to edit the target web map '{target_item.title}' "
            f"(Owner: {target_item.owner})"
        )
    
    return has_edit_rights


def copy_bookmarks_to_webmap(
    source_bookmarks: List[Dict[str, Any]], 
    target_webmap: WebMap, 
    target_item: Any,
    verbose: bool = False
) -> int:
    """
    Copies bookmarks from source to target web map, handling naming conflicts.
    
    Args:
        source_bookmarks (List[Dict[str, Any]]): List of bookmark configurations to copy
        target_webmap (WebMap): Target WebMap object to receive bookmarks
        target_item (Any): Target web map item object for saving changes
        verbose (bool): Enable detailed logging for debugging
        
    Returns:
        int: Number of bookmarks successfully copied
        
    Raises:
        Exception: If update operation fails
    """
    if not source_bookmarks:
        arcpy.AddWarning("No bookmarks found in source webmap to copy")
        return 0
    
    target_definition = target_webmap.definition
    existing_bookmarks = target_definition.get('bookmarks', [])
    existing_bookmark_names = [bookmark.get('name', '') for bookmark in existing_bookmarks]
    
    if verbose:
        arcpy.AddMessage(f"Target webmap has {len(existing_bookmarks)} existing bookmark(s)")
    
    bookmarks_copied = 0
    
    for source_bookmark in source_bookmarks:
        # Create a deep copy to avoid modifying the original
        new_bookmark = copy.deepcopy(source_bookmark)
        original_name = new_bookmark.get('name', 'Unnamed')
        
        # Generate unique name if conflict exists
        unique_name = generate_unique_bookmark_name(original_name, existing_bookmark_names)
        
        if unique_name != original_name:
            arcpy.AddWarning(
                f"Bookmark '{original_name}' already exists. Adding as '{unique_name}'"
            )
            new_bookmark['name'] = unique_name
        
        # Add the new bookmark
        existing_bookmarks.append(new_bookmark)
        existing_bookmark_names.append(unique_name)
        bookmarks_copied += 1
        
        if verbose:
            arcpy.AddMessage(f"Added bookmark: '{unique_name}'")
    
    # Update the webmap definition
    target_definition['bookmarks'] = existing_bookmarks
    
    # Save changes to the web map
    definition_dict = dict(target_definition)
    try:
        target_item.update({'text': json.dumps(definition_dict)})
    except Exception as e:
        arcpy.AddError(f"Failed to update target webmap: {str(e)}")
        raise
    
    arcpy.AddMessage(f"Successfully copied {bookmarks_copied} bookmark(s) to target webmap")
    return bookmarks_copied


def copy_bookmarks_between_webmaps(
    gis: GIS, 
    source_webmap_id: str, 
    target_webmap_ids: List[str],
    verbose: bool = False
) -> Dict[str, int]:
    """
    Main function to copy bookmarks from source webmap to multiple target webmaps.
    
    Args:
        gis (GIS): Authenticated GIS connection object
        source_webmap_id (str): Source web map item ID
        target_webmap_ids (List[str]): List of target web map item IDs
        verbose (bool): Enable detailed logging for debugging
        
    Returns:
        Dict[str, int]: Dictionary mapping target webmap IDs to bookmark counts copied
        
    Raises:
        Exception: Various exceptions for connection, permission, or processing failures
    """
    results = {}
    
    # Add parameter validation section
    if not source_webmap_id:
        arcpy.AddError("Source Web Map ID is required.")
        return results
    if not target_webmap_ids:
        arcpy.AddError("At least one Target Web Map ID is required.")
        return results
    
    # Get source webmap and extract bookmarks
    arcpy.AddMessage("=== Processing Source WebMap ===")
    source_webmap, source_item = get_webmap_and_item(gis, source_webmap_id, verbose)
    source_bookmarks = extract_bookmarks_from_webmap(source_webmap, verbose)
    
    if not source_bookmarks:
        arcpy.AddWarning("Source webmap contains no bookmarks to copy")
        return results
    
    arcpy.AddMessage(f"Found {len(source_bookmarks)} bookmark(s) in source webmap")
    
    # Process each target webmap
    for target_webmap_id in target_webmap_ids:
        arcpy.AddMessage(f"\n=== Processing Target WebMap: {target_webmap_id} ===")
        
        try:
            # Get target webmap
            target_webmap, target_item = get_webmap_and_item(gis, target_webmap_id, verbose)
            
            # Check permissions
            check_edit_permissions(gis, target_item, verbose)
            
            # Copy bookmarks
            bookmarks_copied = copy_bookmarks_to_webmap(
                source_bookmarks, target_webmap, target_item, verbose
            )
            
            results[target_webmap_id] = bookmarks_copied
            arcpy.AddMessage(f"Successfully processed target WebMap: {target_webmap_id}")
            
        except Exception as e:
            arcpy.AddError(f"Failed to process target WebMap {target_webmap_id}: {str(e)}")
            results[target_webmap_id] = 0
    
    return results


def main() -> None:
    """
    Main execution function for the ArcGIS Pro geoprocessing tool.
    Handles parameter parsing, GIS connection, and orchestrates the bookmark copying process.
    
    Parameters (via ArcGIS Pro):
        0: Source WebMap (String) - Format: 'Title [ItemID]'
        1: Target WebMaps (String) - Semicolon-separated, Format: 'Title [ItemID];Title [ItemID]'
        2: Verbose Logging (Boolean) - Enable detailed debugging output
        
    Returns:
        None: Results are communicated via arcpy messaging functions
    """
    try:
        # Parse input parameters
        source_webmap_input = arcpy.GetParameterAsText(0)
        target_webmaps_input = arcpy.GetParameterAsText(1)
        verbose = arcpy.GetParameter(2)  # Boolean parameter
        
        if verbose:
            arcpy.AddMessage("=== VERBOSE MODE ENABLED ===")
            arcpy.AddMessage(f"Raw source input: {source_webmap_input}")
            arcpy.AddMessage(f"Raw target input: {target_webmaps_input}")
        
        # Extract source webmap ID
        source_webmap_id = extract_item_id_from_title(source_webmap_input)
        if not source_webmap_id:
            arcpy.AddError("Invalid source webmap format. Expected: 'Title [ItemID]'")
            return
        
        # Parse and extract target webmap IDs
        raw_target_webmaps = target_webmaps_input.split(";") if target_webmaps_input else []
        target_webmap_ids = [
            item_id
            for raw_input in raw_target_webmaps
            if raw_input and raw_input.strip()
            for item_id in [extract_item_id_from_title(raw_input)]
            if item_id is not None
        ]
        
        # Validate inputs
        if not target_webmap_ids:
            arcpy.AddError("No valid target WebMap IDs provided")
            return
        
        # Log processing parameters
        arcpy.AddMessage(f"Source WebMap ID: {source_webmap_id}")
        arcpy.AddMessage(f"Target WebMap IDs: {', '.join(target_webmap_ids)}")
        arcpy.AddMessage(f"Number of target webmaps: {len(target_webmap_ids)}")
        
        # Connect to GIS
        arcpy.AddMessage("\n=== Establishing GIS Connection ===")
        gis = GIS("pro")
        arcpy.AddMessage(f"Connected to portal as: {gis.properties.user.username}")
        
        if verbose:
            arcpy.AddMessage(f"Portal URL: {gis.url}")
            arcpy.AddMessage(f"User role: {gis.users.me.role}")
        
        # Execute bookmark copying
        results = copy_bookmarks_between_webmaps(
            gis, source_webmap_id, target_webmap_ids, verbose
        )
        
        # Generate summary report
        arcpy.AddMessage("\n=== PROCESSING SUMMARY ===")
        successful_targets = sum(1 for count in results.values() if count > 0)
        failed_targets = len(target_webmap_ids) - len(results)
        total_bookmarks_copied = sum(results.values())
        
        arcpy.AddMessage(f"Target webmaps processed: {len(results)}/{len(target_webmap_ids)}")
        arcpy.AddMessage(f"Successful operations: {successful_targets}")
        arcpy.AddMessage(f"Failed operations: {failed_targets}")
        arcpy.AddMessage(f"Total bookmarks copied: {total_bookmarks_copied}")
        
        if verbose and results:
            arcpy.AddMessage("\nDetailed Results:")
            for webmap_id, count in results.items():
                status = "SUCCESS" if count > 0 else "NO BOOKMARKS COPIED"
                arcpy.AddMessage(f"  {webmap_id}: {count} bookmarks ({status})")
        
        if failed_targets > 0:
            arcpy.AddWarning(
                f"{failed_targets} target webmap(s) failed to process. "
                "Please review error messages above."
            )
        else:
            arcpy.AddMessage("All target webmaps processed successfully!")
            
    except Exception as e:
        arcpy.AddError(f"Critical error occurred: {str(e)}")
        if verbose:
            import traceback
            arcpy.AddError(f"Traceback: {traceback.format_exc()}")


if __name__ == "__main__":

    main()