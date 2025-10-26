"""
Tool Name: Geodatabase Reprojection Tool

Summary: This tool reprojects feature classes from a source geodatabase to a new coordinate system, preserving the structure of feature datasets.

Parameters:
    - Input Geodatabase: Path to the source geodatabase containing feature classes to be reprojected.
    - Output Folder: Destination folder for the newly created reprojected geodatabase.
    - Reconnect Layers: Boolean flag indicating whether to reconnect layers in the current ArcGIS Pro project to the new geodatabase.
    - Spatial Reference: The target spatial reference for reprojecting feature classes.
    - Verbose: Enable detailed logging to ArcGIS Pro messages.

Key Features:
    - Automatically recreates feature datasets in the target geodatabase to maintain organization.
    - Ensures a unique name for the new geodatabase to prevent overwriting existing ones.
    - Can reconnect layers in current projects to the newly reprojected geodatabase.
    - Displays spatial reference details and transformation process information in verbose mode.

Usage: Input the required parameters through ArcGIS Pro to execute the geodatabase reprojection and reconnection process.

Requirements:
    - ArcGIS Pro with access to a valid license.
    - Relevant permissions to the source and destination directories.
    - Access to required spatial reference data.

Date: July 2024
File: reproject_GDB.py
Author: github.com/alex6H
"""

import arcpy
import os
from typing import List, Tuple, Dict


def get_all_feature_classes(gdb_path: str, verbose: bool = False) -> Dict[str, List[str]]:
    """
    Retrieves all feature classes organized by their parent container (root or feature dataset).
    
    Args:
        gdb_path: Path to the source geodatabase
        verbose: Enable detailed logging
    
    Returns:
        Dictionary with keys as feature dataset names (or 'ROOT' for standalone FCs) 
        and values as lists of feature class names
    """
    arcpy.env.workspace = gdb_path
    fc_structure = {'ROOT': []}
    
    # Get standalone feature classes (not in feature datasets)
    standalone_fcs = arcpy.ListFeatureClasses()
    if standalone_fcs:
        fc_structure['ROOT'] = standalone_fcs
        if verbose:
            arcpy.AddMessage(f"Found {len(standalone_fcs)} standalone feature classes")
    
    # Get feature datasets and their feature classes
    feature_datasets = arcpy.ListDatasets(feature_type='feature')
    if feature_datasets:
        for fds in feature_datasets:
            arcpy.env.workspace = os.path.join(gdb_path, fds)
            fcs_in_dataset = arcpy.ListFeatureClasses()
            
            if fcs_in_dataset:
                fc_structure[fds] = fcs_in_dataset
                if verbose:
                    arcpy.AddMessage(f"Feature Dataset '{fds}': {len(fcs_in_dataset)} feature classes")
    
    # Reset workspace
    arcpy.env.workspace = gdb_path
    
    arcpy.AddMessage("Feature classes inventory completed")
    return fc_structure


def create_feature_datasets(new_gdb_path: str, feature_datasets: List[str], 
                           spatial_ref: arcpy.SpatialReference, verbose: bool = False) -> None:
    """
    Creates feature datasets in the new geodatabase with the target spatial reference.
    
    Args:
        new_gdb_path: Path to the target geodatabase
        feature_datasets: List of feature dataset names to create
        spatial_ref: Target spatial reference for the feature datasets
        verbose: Enable detailed logging
    """
    for fds_name in feature_datasets:
        if fds_name == 'ROOT':
            continue
            
        fds_path = os.path.join(new_gdb_path, fds_name)
        arcpy.management.CreateFeatureDataset(
            out_dataset_path=new_gdb_path,
            out_name=fds_name,
            spatial_reference=spatial_ref
        )
        
        if verbose:
            arcpy.AddMessage(f"Created feature dataset: {fds_name}")


def reproject_feature_classes(gdb_path: str, fc_structure: Dict[str, List[str]], 
                             output_folder: str, spatial_ref: arcpy.SpatialReference,
                             verbose: bool = False) -> str:
    """
    Reprojects all feature classes to a new geodatabase, preserving feature dataset structure.
    
    Args:
        gdb_path: Source geodatabase path
        fc_structure: Dictionary of feature classes organized by container
        output_folder: Folder where new geodatabase will be created
        spatial_ref: Target spatial reference
        verbose: Enable detailed logging
    
    Returns:
        Path to the newly created geodatabase
    """
    arcpy.AddMessage("----------------------")
    
    # Create new geodatabase with unique name
    base_gdb_name = os.path.basename(gdb_path)[:-4] + '_Reprojected.gdb'
    new_gdb_path = os.path.join(output_folder, base_gdb_name)
    
    counter = 1
    while arcpy.Exists(new_gdb_path):
        arcpy.AddWarning(f"Geodatabase {new_gdb_path} exists. Incrementing name.")
        new_gdb_path = os.path.join(output_folder, 
                                     f"{os.path.basename(gdb_path)[:-4]}_Reprojected_{counter}.gdb")
        counter += 1
    
    # Create new geodatabase
    arcpy.CreateFileGDB_management(
        out_folder_path=os.path.dirname(new_gdb_path),
        out_name=os.path.basename(new_gdb_path),
        out_version='CURRENT'
    )
    arcpy.AddMessage(f"Created geodatabase: {new_gdb_path}")
    
    # Create feature datasets first
    feature_datasets = [fds for fds in fc_structure.keys() if fds != 'ROOT']
    if feature_datasets:
        create_feature_datasets(new_gdb_path, feature_datasets, spatial_ref, verbose)
    
    # Reproject feature classes
    total_fcs = sum(len(fcs) for fcs in fc_structure.values())
    arcpy.AddMessage(f"Reprojecting {total_fcs} feature classes...")
    
    for container, fc_list in fc_structure.items():
        for fc in fc_list:
            # Build input path
            if container == 'ROOT':
                input_fc = os.path.join(gdb_path, fc)
                output_fc = os.path.join(new_gdb_path, fc)
            else:
                input_fc = os.path.join(gdb_path, container, fc)
                output_fc = os.path.join(new_gdb_path, container, fc)
            
            # Reproject
            arcpy.management.Project(
                in_dataset=input_fc,
                out_dataset=output_fc,
                out_coor_system=spatial_ref,
                transform_method=""
            )
            
            if verbose:
                location = f"in {container}" if container != 'ROOT' else "at root"
                arcpy.AddMessage(f"Reprojected: {fc} ({location})")
    
    arcpy.AddMessage("Reprojection completed successfully")
    return new_gdb_path


def reconnect_layers(old_gdb: str, new_gdb: str, verbose: bool = False) -> None:
    """
    Reconnects layers in the current ArcGIS Pro project to the new geodatabase.
    
    Args:
        old_gdb: Original geodatabase path
        new_gdb: New reprojected geodatabase path
        verbose: Enable detailed logging
    """
    arcpy.AddMessage("----------------------")
    arcpy.AddMessage("Reconnecting layers to new geodatabase...")
    
    aprx = arcpy.mp.ArcGISProject("CURRENT")
    reconnected_count = 0
    
    for mp in aprx.listMaps():
        for lyr in mp.listLayers():
            if not lyr.supports("DATASOURCE"):
                continue
            
            con_prop = lyr.connectionProperties
            if not con_prop or 'connection_info' not in con_prop:
                continue
            
            if 'database' not in con_prop['connection_info']:
                continue
            
            if old_gdb in con_prop['connection_info']['database']:
                con_prop['connection_info']['database'] = con_prop['connection_info']['database'].replace(
                    old_gdb, new_gdb
                )
                lyr.updateConnectionProperties(lyr.connectionProperties, con_prop)
                reconnected_count += 1
                
                if verbose:
                    arcpy.AddMessage(f"Reconnected: {lyr.name}")
    
    arcpy.AddMessage(f"Reconnected {reconnected_count} layers")


def add_gdb_to_project(aprx: arcpy.mp.ArcGISProject, gdb_path: str, 
                       is_default: bool = False, verbose: bool = False) -> None:
    """
    Adds a geodatabase to the current ArcGIS Pro project.
    
    Args:
        aprx: ArcGIS Project object
        gdb_path: Path to the geodatabase to add
        is_default: Set as default geodatabase
        verbose: Enable detailed logging
    """
    gdbs = aprx.databases
    gdbs.append({'databasePath': gdb_path, 'isDefaultDatabase': is_default})
    aprx.updateDatabases(gdbs)
    
    if verbose:
        arcpy.AddMessage(f"Added geodatabase to project: {gdb_path}")


if __name__ == "__main__":
    
    try:
        # Get parameters (matching YOUR tool parameter order)
        gdb_path = arcpy.GetParameterAsText(0)  # Input Geodatabase
        output_folder = arcpy.GetParameterAsText(1)  # Output Folder
        reconnect_flag = arcpy.GetParameterAsText(2)  # Reconnect layers (Boolean at index 2)
        spatial_ref_param = arcpy.GetParameter(3)  # Spatial Reference (at index 3)
        verbose = arcpy.GetParameter(4)  # Verbose mode (Boolean)
        
        # Debug: Show what we received
        arcpy.AddMessage(f"DEBUG - Spatial ref parameter type: {type(spatial_ref_param)}")
        arcpy.AddMessage(f"DEBUG - Spatial ref parameter value: {spatial_ref_param}")
        
        # Ensure spatial reference is a proper SpatialReference object
        if spatial_ref_param is None or spatial_ref_param == '':
            arcpy.AddError("Spatial Reference parameter is empty or None")
            raise ValueError("Spatial Reference is required")
        
        if isinstance(spatial_ref_param, str):
            arcpy.AddMessage(f"Converting string to SpatialReference: {spatial_ref_param}")
            spatial_ref = arcpy.SpatialReference(spatial_ref_param)
        elif isinstance(spatial_ref_param, int):
            arcpy.AddMessage(f"Converting int to SpatialReference: {spatial_ref_param}")
            spatial_ref = arcpy.SpatialReference(spatial_ref_param)
        else:
            spatial_ref = spatial_ref_param
        
        # Validate spatial reference
        arcpy.AddMessage(f"Spatial Reference Name: {spatial_ref.name}")
        arcpy.AddMessage(f"Spatial Reference Factory Code: {spatial_ref.factoryCode}")
        
        if verbose:
            arcpy.AddMessage(f"Target Spatial Reference: {spatial_ref.name} (EPSG: {spatial_ref.factoryCode})")
        
        # Inventory feature classes
        fc_structure = get_all_feature_classes(gdb_path, verbose)
        
        # Reproject to new geodatabase
        new_gdb_path = reproject_feature_classes(
            gdb_path, fc_structure, output_folder, spatial_ref, verbose
        )
        
        # Open current project
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        
        # Add new GDB to project
        add_gdb_to_project(aprx, new_gdb_path, is_default=False, verbose=verbose)
        
        # Reconnect layers if requested
        if reconnect_flag.lower() == 'true':
            reconnect_layers(gdb_path, new_gdb_path, verbose)
        
        # Save project
        aprx.save()
        arcpy.AddMessage("----------------------")
        arcpy.AddMessage("Project saved successfully")
        arcpy.AddMessage("----------------------")
        arcpy.AddMessage("Process completed!")
        
    except Exception as e:
        arcpy.AddError(f"Error: {str(e)}")
        raise