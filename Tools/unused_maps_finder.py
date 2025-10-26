"""
Tool Name: Unused Maps Finder

Summary: This tool evaluates the usage of maps within layouts of an ArcGIS Pro project, identifying maps that are actively used and those that are orphaned, and provides a comprehensive report of map-to-layout relationships.

Parameters:
    - Project Path: Path to the ArcGIS Pro project (.aprx) file. If empty, the current project is used.
    
Key Features:
    - Analyzes map-to-layout associations within the ArcGIS Pro project.
    - Identifies unused maps to help streamline project management.
    - Generates a detailed report with summary statistics to the ArcGIS Pro messages.

Usage: Run the tool with the appropriate project path to assess map usage within project layouts.

Requirements:
    - ArcGIS Pro with appropriate licenses and access permissions.
    - Valid path to the ArcGIS project file or access to the current project session.

Date: July 2024
File: unused_maps_finder.py
Author: github.com/alex6H

"""

import arcpy
import os
import sys
import datetime
from typing import List, Dict, Set, Tuple

def validate_project(project_path: str) -> arcpy.mp.ArcGISProject:
    """
    Validate and load ArcGIS Pro project.
    
    Args:
        project_path: Path to .aprx file or empty for current project
        
    Returns:
        ArcGISProject object
        
    Raises:
        ValueError: If project cannot be loaded
    """
    try:
        if not project_path or project_path.strip() == "":
            arcpy.AddMessage("Loading current ArcGIS Pro project")
            aprx = arcpy.mp.ArcGISProject("CURRENT")
        else:
            if not os.path.exists(project_path):
                raise ValueError(f"Project file not found: {project_path}")
            arcpy.AddMessage(f"Loading project: {os.path.basename(project_path)}")
            aprx = arcpy.mp.ArcGISProject(project_path)
        
        return aprx
        
    except Exception as e:
        arcpy.AddError(f"Failed to load project: {str(e)}")
        raise


def analyze_map_usage(aprx: arcpy.mp.ArcGISProject) -> Tuple[Dict[str, Set[str]], List[str]]:
    """
    Analyze which maps are used in which layouts.
    
    Args:
        aprx: ArcGIS Pro project object
        
    Returns:
        Tuple of (map_to_layouts dict, all_map_names list)
    """
    all_maps = aprx.listMaps()
    all_layouts = aprx.listLayouts()
    
    # Validate project has maps
    if not all_maps:
        arcpy.AddWarning("Project contains no maps")
        return {}, []
    
    # Initialize map usage tracking
    map_to_layouts = {map_obj.name: set() for map_obj in all_maps}
    
    # Scan all layouts for map usage
    for layout in all_layouts:
        for map_frame in layout.listElements("MAPFRAME_ELEMENT"):
            if map_frame.map:
                map_name = map_frame.map.name
                if map_name in map_to_layouts:
                    map_to_layouts[map_name].add(layout.name)
    
    return map_to_layouts, [map_obj.name for map_obj in all_maps]


def report_results(map_to_layouts: Dict[str, Set[str]], all_map_names: List[str]) -> None:
    """
    Display formatted map usage report.
    
    Args:
        map_to_layouts: Dictionary mapping map names to sets of layout names
        all_map_names: List of all map names in project
    """
    if not all_map_names:
        arcpy.AddMessage("=" * 80)
        arcpy.AddMessage("No maps found in project")
        arcpy.AddMessage("=" * 80)
        return
    
    # Separate used and unused maps
    used_maps = {name: layouts for name, layouts in map_to_layouts.items() if layouts}
    unused_maps = {name: layouts for name, layouts in map_to_layouts.items() if not layouts}
    
    arcpy.AddMessage("=" * 80)
    arcpy.AddMessage("MAP USAGE IN LAYOUTS REPORT")
    arcpy.AddMessage("=" * 80)
    
    # Report used maps
    if used_maps:
        arcpy.AddMessage(f"\nMAPS USED IN LAYOUTS ({len(used_maps)} maps)")
        arcpy.AddMessage("-" * 80)
        
        for map_name in sorted(used_maps.keys()):
            layouts = sorted(used_maps[map_name])
            arcpy.AddMessage(f"\n✓ {map_name}")
            for layout_name in layouts:
                arcpy.AddMessage(f"  → Layout: {layout_name}")
    
    # Report unused maps
    if unused_maps:
        arcpy.AddMessage(f"\n\nMAPS NOT USED IN ANY LAYOUT ({len(unused_maps)} maps)")
        arcpy.AddMessage("-" * 80)
        
        for map_name in sorted(unused_maps.keys()):
            arcpy.AddMessage(f"✗ {map_name}")
    else:
        arcpy.AddMessage("\n\n✓ All maps are used in at least one layout")
    
    # Summary statistics
    arcpy.AddMessage("\n" + "=" * 80)
    arcpy.AddMessage(f"SUMMARY: {len(used_maps)}/{len(all_map_names)} maps in use | "
                    f"{len(unused_maps)} unused maps")
    arcpy.AddMessage("=" * 80)


if __name__ == "__main__":
    try:
        # Get parameters
        project_path = arcpy.GetParameterAsText(0)
        
        # Validate and load project
        aprx = validate_project(project_path)
        
        # Analyze map usage
        arcpy.AddMessage("\nAnalyzing map usage in layouts...")
        map_to_layouts, all_map_names = analyze_map_usage(aprx)
        
        # Report results
        report_results(map_to_layouts, all_map_names)
        
        arcpy.AddMessage("\n✓ Analysis complete!")
        
    except Exception as e:
        arcpy.AddError(f"Tool execution failed: {str(e)}")
        raise


