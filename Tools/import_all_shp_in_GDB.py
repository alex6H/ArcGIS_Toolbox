"""
Tool Name: Shapefile Importer and Connector Tool

Summary: This tool processes an ArcGIS Pro project to extract feature layer paths, import shapefiles into a specified File Geodatabase, and optionally reconnect these shapefiles to corresponding feature classes within the geodatabase.

Parameters:
    - Workspace: Path to the geodatabase where feature layers are to be imported.
    - Spatial Reference: Target spatial reference for the feature dataset.
    - Feature Dataset Name: Name of the feature dataset within the geodatabase.
    - Reconnect Layers: Boolean flag indicating whether to reconnect shapefiles to feature classes in the geodatabase.
    - Verbose: Enable detailed logging to ArcGIS Pro messages.

Key Features:
    - Automatically filters and imports shapefile layers from the current project into the specified geodatabase.
    - Creates feature datasets if they do not exist within the target geodatabase.
    - Provides an option to reconnect shapefiles to the geodatabase feature classes for updated project links.

Usage: Input the required parameters through ArcGIS Pro to execute the shapefile import and reconnection process.

Requirements:
    - ArcGIS Pro with access to a valid license.
    - Permissions to edit the project and access the specified directories.
    - Valid input for geodatabase path and spatial reference.

Date: July 2024
File: import_all_shp_in_GDB.py
Author: github.com/alex6H
"""

import os
import arcpy
from typing import List


def find_featurelayer_paths(aprx: arcpy.mp.ArcGISProject, verbose: bool = False) -> List[str]:
    """
    Extracts unique file paths of all feature layers within an ArcGIS Pro project.

    Args:
        aprx: The ArcGIS Pro project object
        verbose: Enable detailed logging

    Returns:
        List of unique file paths for all feature layers in the project
    """
    layer_paths = []
    maps = aprx.listMaps()
    
    arcpy.AddMessage(f"Found {len(maps)} map(s) in the project")   
    arcpy.AddMessage("----------------------")

    for map_obj in maps:
        for lyr in map_obj.listLayers():
            if not lyr.supports("DATASOURCE"):
                continue
            
            try:
                desc = arcpy.Describe(lyr)
                if desc.dataType == 'FeatureLayer':
                    layer_paths.append(desc.catalogPath)
            except Exception as e:
                if verbose:
                    arcpy.AddWarning(f"Could not describe layer {lyr.name}: {str(e)}")
    
    # Remove duplicates and empty strings
    layer_paths = list(set([path for path in layer_paths if path]))
    
    return layer_paths


def import_shapefiles_to_gdb(all_fl_paths: List[str], gdb_path: str, 
                            feature_dataset_name: str, spatial_ref: arcpy.SpatialReference,
                            verbose: bool = False) -> List[str]:
    """
    Imports shapefiles to a specified geodatabase feature dataset.

    Args:
        all_fl_paths: List of all feature layer file paths
        gdb_path: Path to the target geodatabase
        feature_dataset_name: Name of the feature dataset to create/use
        spatial_ref: Spatial reference for the feature dataset
        verbose: Enable detailed logging

    Returns:
        List of shapefile paths that were successfully imported
    """
    # Filter for shapefiles only
    shp_paths = [path for path in all_fl_paths if path.lower().endswith(".shp")]
    
    if len(shp_paths) == 0:
        arcpy.AddMessage("No shapefiles found in project layers")
        return []
    
    arcpy.AddMessage(f"Found {len(shp_paths)} shapefile(s) to import")
    feature_dataset_path = os.path.join(gdb_path, feature_dataset_name)
    
    # Create feature dataset if needed
    if arcpy.Exists(feature_dataset_path):
        arcpy.AddMessage(f"Feature dataset '{feature_dataset_name}' already exists")
    else:
        arcpy.management.CreateFeatureDataset(
            out_dataset_path=gdb_path,
            out_name=feature_dataset_name,
            spatial_reference=spatial_ref
        )
        arcpy.AddMessage(f"Created feature dataset: {feature_dataset_name}")
    
    imported_shp_paths = []
    skipped_count = 0
    
    # Import shapefiles
    for shp_path in shp_paths:
        fc_name = os.path.basename(shp_path)[:-4]
        fc_path = os.path.join(feature_dataset_path, fc_name)
        
        if arcpy.Exists(fc_path):
            arcpy.AddWarning(f"Feature class already exists, skipping: {fc_name}")
            skipped_count += 1
            continue
        
        try:
            arcpy.conversion.FeatureClassToGeodatabase(
                Input_Features=shp_path,
                Output_Geodatabase=feature_dataset_path
            )
            imported_shp_paths.append(shp_path)
            
            if verbose:
                arcpy.AddMessage(f"Imported: {fc_name}")
                
        except Exception as e:
            arcpy.AddError(f"Failed to import {fc_name}: {str(e)}")
    
    arcpy.AddMessage(f"Successfully imported: {len(imported_shp_paths)}")
    if skipped_count > 0:
        arcpy.AddMessage(f"Skipped (already exist): {skipped_count}")
    
    return imported_shp_paths



def reconnect_shapefiles_to_gdb(aprx: arcpy.mp.ArcGISProject, gdb_path: str, 
                                feature_dataset_name: str, shp_paths: List[str],
                                verbose: bool = False) -> None:
    """
    Reconnects shapefile layers in the project to their corresponding feature classes in the GDB.

    Args:
        aprx: The ArcGIS Pro project object
        gdb_path: Path to the geodatabase
        feature_dataset_name: Name of the feature dataset containing the feature classes
        shp_paths: List of shapefile paths that were imported
        verbose: Enable detailed logging
    """
    if not shp_paths:
        arcpy.AddMessage("No shapefiles to reconnect")
        return
    
    arcpy.AddMessage("----------------------")
    arcpy.AddMessage("Reconnecting shapefile layers to geodatabase...")
    
    # Create lookup dictionary for faster matching
    shp_basenames = {os.path.basename(path)[:-4].lower(): path for path in shp_paths}
    reconnected_count = 0
    
    for map_obj in aprx.listMaps():
        for lyr in map_obj.listLayers():
            if not lyr.supports("DATASOURCE"):
                continue
            
            try:
                # Get current connection properties
                con_prop = lyr.connectionProperties
                
                if verbose:
                    arcpy.AddMessage(f"Checking layer: {lyr.name}")
                    arcpy.AddMessage(f"  Current connection: {con_prop}")
                
                # Check if it's a shapefile connection
                if not con_prop or 'connection_info' not in con_prop:
                    continue
                
                # Look for workspace_factory or check dataset path
                current_path = None
                if 'dataset' in con_prop:
                    current_path = con_prop['dataset']
                elif 'connection_info' in con_prop and 'database' in con_prop['connection_info']:
                    current_path = con_prop['connection_info'].get('database', '')
                
                # Skip if not a shapefile
                if not current_path or not current_path.lower().endswith('.shp'):
                    continue
                
                shp_name = os.path.basename(current_path)[:-4]
                
                if verbose:
                    arcpy.AddMessage(f"  Shapefile name: {shp_name}")
                
                # Check if this shapefile was imported
                if shp_name.lower() not in shp_basenames:
                    if verbose:
                        arcpy.AddMessage(f"  Not in import list, skipping")
                    continue
                
                # Build the new feature class path
                fc_path = os.path.join(gdb_path, feature_dataset_name, shp_name)
                
                if not arcpy.Exists(fc_path):
                    arcpy.AddWarning(f"Feature class not found in GDB: {shp_name}")
                    continue
                
                # Build new connection properties - must include feature dataset in connection_info
                new_conn_props = {
                    'connection_info': {
                        'database': gdb_path,
                        'feature_dataset': feature_dataset_name
                    },
                    'workspace_factory': 'File Geodatabase',
                    'dataset': shp_name
                }
                
                if verbose:
                    arcpy.AddMessage(f"  Old connection: {con_prop}")
                    arcpy.AddMessage(f"  New connection: {new_conn_props}")
                
                # Update the connection
                result = lyr.updateConnectionProperties(con_prop, new_conn_props)
                
                if verbose:
                    arcpy.AddMessage(f"  Update result: {result}")
                    # Verify the update
                    updated_con_prop = lyr.connectionProperties
                    arcpy.AddMessage(f"  Verified connection: {updated_con_prop}")
                
                # Update layer name to remove .shp extension
                if lyr.name.lower().endswith('.shp'):
                    lyr.name = lyr.name[:-4]
                
                reconnected_count += 1
                arcpy.AddMessage(f"Reconnected: {shp_name}")
                    
            except Exception as e:
                arcpy.AddError(f"Failed to reconnect layer {lyr.name}: {str(e)}")
                if verbose:
                    import traceback
                    arcpy.AddError(traceback.format_exc())
    
    arcpy.AddMessage(f"Successfully reconnected {reconnected_count} layer(s)")
    aprx.save()
    arcpy.AddMessage("Project saved")


if __name__ == "__main__":
    
    try:
        # Get parameters
        gdb_path = arcpy.GetParameterAsText(0)  # Workspace
        spatial_ref = arcpy.GetParameter(1)  # Spatial Reference
        feature_dataset_name = arcpy.GetParameterAsText(2)  # String (Feature Dataset Name)
        reconnect_flag = arcpy.GetParameter(3)  # Boolean
        verbose = arcpy.GetParameter(4)  # Boolean
        
        # Validate inputs
        if not arcpy.Exists(gdb_path):
            arcpy.AddError(f"Geodatabase does not exist: {gdb_path}")
            raise ValueError("Invalid geodatabase path")
        
        if not feature_dataset_name:
            feature_dataset_name = "imported_shapefiles"
            arcpy.AddMessage(f"Using default feature dataset name: {feature_dataset_name}")
        
        # Get current project
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        
        # Find all feature layer paths
        all_fl_paths = find_featurelayer_paths(aprx, verbose)
        arcpy.AddMessage(f"Total feature layers found: {len(all_fl_paths)}")
        
        # Import shapefiles to GDB
        imported_shp_paths = import_shapefiles_to_gdb(
            all_fl_paths, gdb_path, feature_dataset_name, spatial_ref, verbose
        )
        
        # Reconnect if requested
        if reconnect_flag and imported_shp_paths:
            reconnect_shapefiles_to_gdb(
                aprx, gdb_path, feature_dataset_name, imported_shp_paths, verbose
            )
        
        arcpy.AddMessage("----------------------")
        arcpy.AddMessage("Process completed successfully!")
        
    except Exception as e:
        arcpy.AddError(f"Error: {str(e)}")
        raise