"""
Tool Name: Unused Feature Class Finder Tool

Summary: This tool identifies feature classes and other assets that are not currently in use within specified ArcGIS Pro projects, helping users streamline geodatabase management by pinpointing unused data.

Parameters:
    - Geodatabase Paths: Semicolon-separated paths to geodatabases containing feature classes and other assets.
    - Project Paths: Semicolon-separated paths to ArcGIS Pro project files. If empty, the current project is used.
    - Verbose: Enable detailed logging to ArcGIS Pro messages.

Key Features:
    - Validates provided geodatabase and project file paths for accuracy.
    - Collects and analyzes map data source usage across specified projects.
    - Generates a comprehensive report listing unused feature classes, tables, and raster datasets within the geodatabases.

Usage: Execute the tool with specified paths to evaluate asset usage across ArcGIS projects and optimize geodatabase content.

Requirements:
    - ArcGIS Pro with relevant permissions and licenses.
    - Valid input paths for geodatabases and project files.

Date: July 2024
File: unused_feature_class_finder.py
Author: github.com/alex6H
"""
import arcpy
import os
from typing import List, Set, Tuple
        
def validate_inputs(gdb_paths: List[str], aprx_paths: List[str], verbose: bool) -> Tuple[List[str], List[str]]:
    """
    Validate geodatabase and project file paths.
    
    Args:
        gdb_paths: List of geodatabase paths
        aprx_paths: List of ArcGIS Pro project paths
        verbose: Enable detailed logging
        
    Returns:
        Tuple of validated (gdb_paths, aprx_paths)
    """
    valid_gdbs = []
    valid_aprxs = []
    
    # Validate geodatabases
    for gdb in gdb_paths:
        gdb_clean = gdb.replace("'", "").strip()
        if arcpy.Exists(gdb_clean):
            valid_gdbs.append(gdb_clean)
            if verbose:
                arcpy.AddMessage(f"✓ Valid GDB: {gdb_clean}")
        else:
            arcpy.AddWarning(f"✗ GDB not found: {gdb_clean}")
    
    # Validate APRX files
    for aprx in aprx_paths:
        aprx_clean = aprx.replace("'", "").strip()
        if aprx_clean and os.path.exists(aprx_clean):
            valid_aprxs.append(aprx_clean)
            if verbose:
                arcpy.AddMessage(f"✓ Valid APRX: {aprx_clean}")
        elif aprx_clean:
            arcpy.AddWarning(f"✗ APRX not found: {aprx_clean}")
    
    if not valid_gdbs:
        arcpy.AddError("No valid geodatabases found")
        raise ValueError("No valid geodatabases")
    
    return valid_gdbs, valid_aprxs


def collect_maps_from_projects(aprx_paths: List[str], verbose: bool) -> List:
    """
    Collect all maps from specified ArcGIS Pro projects.
    
    Args:
        aprx_paths: List of project paths (empty list uses current project)
        verbose: Enable detailed logging
        
    Returns:
        List of map objects
    """
    maps = []
    
    if not aprx_paths:
        arcpy.AddMessage("Using current ArcGIS Pro project")
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        maps = aprx.listMaps()
    else:
        arcpy.AddMessage(f"Loading {len(aprx_paths)} project(s)")
        for aprx_path in aprx_paths:
            try:
                aprx = arcpy.mp.ArcGISProject(aprx_path)
                project_maps = aprx.listMaps()
                maps.extend(project_maps)
                if verbose:
                    arcpy.AddMessage(f"  → {len(project_maps)} map(s) from {os.path.basename(aprx_path)}")
            except Exception as e:
                arcpy.AddWarning(f"Failed to load project {aprx_path}: {str(e)}")
    
    arcpy.AddMessage(f"Total maps loaded: {len(maps)}")
    return maps


def collect_used_assets(maps: List, verbose: bool) -> Set[str]:
    """
    Collect all data sources referenced in map layers.
    
    Args:
        maps: List of map objects
        verbose: Enable detailed logging
        
    Returns:
        Set of catalog paths for used assets
    """
    used_assets = set()
    
    for map_obj in maps:
        if verbose:
            arcpy.AddMessage(f"Scanning map: {map_obj.name}")
        
        for lyr in map_obj.listLayers():
            if lyr.supports("dataSource"):
                try:
                    desc = arcpy.Describe(lyr)
                    if desc.dataType in ['FeatureLayer', 'Table', 'RasterLayer', 'RasterDataset']:
                        used_assets.add(desc.catalogPath)
                        if verbose:
                            arcpy.AddMessage(f"  ✓ Used: {desc.catalogPath}")
                except Exception as e:
                    if verbose:
                        arcpy.AddWarning(f"  ✗ Could not describe layer: {lyr.name}")
    
    arcpy.AddMessage(f"Total assets in use: {len(used_assets)}")
    return used_assets


def collect_all_assets(gdb_paths: List[str], verbose: bool) -> dict:
    """
    Collect all datasets from geodatabases.
    
    Args:
        gdb_paths: List of geodatabase paths
        verbose: Enable detailed logging
        
    Returns:
        Dictionary with asset types as keys and sets of paths as values
    """
    assets = {
        'FeatureClass': set(),
        'Table': set(),
        'RasterDataset': set()
    }
    
    for gdb_path in gdb_paths:
        arcpy.AddMessage(f"Scanning GDB: {os.path.basename(gdb_path)}")
        
        # Scan feature classes
        for dirpath, dirnames, filenames in arcpy.da.Walk(gdb_path, datatype="FeatureClass"):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                assets['FeatureClass'].add(full_path)
        
        # Scan tables
        for dirpath, dirnames, filenames in arcpy.da.Walk(gdb_path, datatype="Table"):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                assets['Table'].add(full_path)
        
        # Scan rasters
        for dirpath, dirnames, filenames in arcpy.da.Walk(gdb_path, datatype="RasterDataset"):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                assets['RasterDataset'].add(full_path)
        
        if verbose:
            arcpy.AddMessage(f"  → {len(assets['FeatureClass'])} FCs, {len(assets['Table'])} tables, {len(assets['RasterDataset'])} rasters")
    
    return assets


def compute_unused_assets(all_assets: dict, used_assets: Set[str]) -> dict:
    """
    Compute unused assets by type.
    
    Args:
        all_assets: Dictionary of all assets by type
        used_assets: Set of used asset paths
        
    Returns:
        Dictionary of unused assets by type
    """
    unused = {}
    for asset_type, asset_set in all_assets.items():
        unused[asset_type] = sorted(asset_set - used_assets)
    return unused


def report_results(unused_assets: dict, verbose: bool) -> None:
    """
    Display formatted results to console.
    
    Args:
        unused_assets: Dictionary of unused assets by type
        verbose: Enable detailed logging
    """
    arcpy.AddMessage("=" * 80)
    arcpy.AddMessage("UNUSED GEODATABASE ASSETS REPORT")
    arcpy.AddMessage("=" * 80)
    
    total_unused = sum(len(items) for items in unused_assets.values())
    
    if total_unused == 0:
        arcpy.AddMessage("✓ All geodatabase assets are in use!")
        arcpy.AddMessage("=" * 80)
        return
    
    for asset_type, items in unused_assets.items():
        if items:
            arcpy.AddMessage(f"\n{asset_type}: {len(items)} unused")
            arcpy.AddMessage("-" * 80)
            
            for item in items:
                # Format path for better readability
                if "\\" in item:
                    parts = item.split("\\")
                    gdb_name = next((p for p in parts if p.endswith('.gdb')), '')
                    relative_path = "\\".join(parts[parts.index(gdb_name):]) if gdb_name else item
                    arcpy.AddMessage(f"  • {relative_path}")
                else:
                    arcpy.AddMessage(f"  • {item}")
    
    arcpy.AddMessage("=" * 80)
    arcpy.AddMessage(f"TOTAL UNUSED ASSETS: {total_unused}")
    arcpy.AddMessage("=" * 80)


if __name__ == "__main__":
    try:
        # Get parameters
        gdb_paths = arcpy.GetParameterAsText(0).split(';')
        aprx_paths = arcpy.GetParameterAsText(1).split(';')
        verbose = arcpy.GetParameter(2) 
        
        # Validate inputs
        arcpy.AddMessage("Validating inputs...")
        valid_gdbs, valid_aprxs = validate_inputs(gdb_paths, aprx_paths, verbose)
        
        # Collect maps
        arcpy.AddMessage("\nCollecting maps from projects...")
        maps = collect_maps_from_projects(valid_aprxs, verbose)
        
        if not maps:
            arcpy.AddWarning("No maps found in projects")
        
        # Collect used assets
        arcpy.AddMessage("\nIdentifying used assets...")
        used_assets = collect_used_assets(maps, verbose)
        
        # Collect all assets
        arcpy.AddMessage("\nScanning geodatabases...")
        all_assets = collect_all_assets(valid_gdbs, verbose)
        
        # Compute unused
        arcpy.AddMessage("\nComputing unused assets...")
        unused_assets = compute_unused_assets(all_assets, used_assets)
        
        # Report results
        report_results(unused_assets, verbose)
        
        arcpy.AddMessage("\n✓ Geoprocessing complete!")
        
    except Exception as e:
        arcpy.AddError(f"Tool execution failed: {str(e)}")
        raise
