"""
Tool Name: Export Maps to MAPX Tool

Summary: This tool exports all maps from a specified ArcGIS Pro project to individual .mapx files, facilitating the sharing and reuse of map configurations.

Parameters:
    - ArcGIS Pro Project Path: Path to the ArcGIS Pro project (.aprx). If empty, the currently open project is used.
    - Output Directory: Directory where the exported .mapx files will be saved.

Key Features:
    - Automatically identifies and exports all maps within an ArcGIS Pro project.
    - Converts map names into filesystem-safe filenames to ensure compatibility.
    - Provides detailed progress messages during the export process.

Usage: Provide the project path and destination directory to execute the map export operation.

Requirements:
    - ArcGIS Pro with relevant permissions and licenses.
    - Valid paths for the project file and output directory.

Date: July 2024
File: export_all_maps_into_MAPX.py
Author: github.com/alex6H
"""
"""
ArcGIS Pro tool to export all maps from a project to individual .mapx files.

This script exports each map in an ArcGIS Pro project as a standalone map package (.mapx),
useful for sharing individual maps or creating backups of map configurations.
"""

import os
import arcpy
from typing import Optional


def sanitize_filename(name: str) -> str:
    """
    Converts a map name into a valid filename by replacing invalid characters.
    
    Args:
        name: Original map name
        
    Returns:
        Sanitized filename safe for file systems
    """
    return "".join(c if c.isalnum() or c in (' ', '-', '_') else "_" for c in name)


def export_maps_to_mapx(aprx: arcpy.mp.ArcGISProject, output_dir: str) -> int:
    """
    Exports all maps from an ArcGIS Pro project to individual .mapx files.
    
    Args:
        aprx: ArcGIS Pro project object
        output_dir: Directory where .mapx files will be saved
        
    Returns:
        Number of maps successfully exported
    """
    if not os.path.exists(output_dir):
        arcpy.AddError(f"Output directory does not exist: {output_dir}")
        raise ValueError("Invalid output directory")
    
    maps = aprx.listMaps()
    
    if not maps:
        arcpy.AddWarning("No maps found in the project")
        return 0
    
    arcpy.AddMessage(f"Found {len(maps)} map(s) to export")
    arcpy.AddMessage("----------------------")
    
    exported_count = 0
    skipped_count = 0
    
    for map_obj in maps:
        # Skip unnamed maps
        if not map_obj.name or not map_obj.name.strip():
            arcpy.AddWarning("Skipped unnamed map")
            skipped_count += 1
            continue
        
        try:
            # Create valid filename
            valid_name = sanitize_filename(map_obj.name)
            mapx_path = os.path.join(output_dir, f"{valid_name}.mapx")
            
            # Check if file already exists
            if os.path.exists(mapx_path):
                arcpy.AddWarning(f"File already exists, overwriting: {valid_name}.mapx")
            
            # Export the map
            map_obj.exportToMAPX(mapx_path)
            exported_count += 1
            
            arcpy.AddMessage(f"Exported: {valid_name}.mapx")
                
        except Exception as e:
            arcpy.AddError(f"Failed to export map '{map_obj.name}': {str(e)}")
            skipped_count += 1
    
    arcpy.AddMessage("----------------------")
    arcpy.AddMessage(f"Successfully exported: {exported_count}")
    if skipped_count > 0:
        arcpy.AddMessage(f"Skipped/Failed: {skipped_count}")
    
    return exported_count


if __name__ == "__main__":
    
    try:
        # Get parameters
        aprx_path = arcpy.GetParameterAsText(0)
        output_dir = arcpy.GetParameterAsText(1)  
        
        # Open project
        if not aprx_path or aprx_path.strip() == "":
            arcpy.AddMessage("Using current ArcGIS Pro project")
            aprx = arcpy.mp.ArcGISProject("CURRENT")
        else:
            if not os.path.exists(aprx_path):
                arcpy.AddError(f"Project file not found: {aprx_path}")
                raise ValueError("Invalid project path")
            arcpy.AddMessage(f"Opening project: {aprx_path}")
            aprx = arcpy.mp.ArcGISProject(aprx_path)
        
        # Export maps
        exported_count = export_maps_to_mapx(aprx, output_dir)
        
        if exported_count > 0:
            arcpy.AddMessage("Export completed successfully!")
        else:
            arcpy.AddWarning("No maps were exported")
        
    except Exception as e:
        arcpy.AddError(f"Error: {str(e)}")
        raise