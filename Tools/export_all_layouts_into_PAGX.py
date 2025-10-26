"""
Tool Name: Export Layouts to PAGX Tool

Summary: This tool exports all layouts from a specified ArcGIS Pro project to individual .pagx files, facilitating the sharing and reuse of layout configurations.

Parameters:
    - ArcGIS Pro Project Path: Full path to the ArcGIS Pro project (.aprx) file. If empty, the current project is used.
    - Output Directory: Directory where the .pagx files will be saved.

Key Features:
    - Automatically detects and exports all layouts within the specified ArcGIS Pro project.
    - Saves each layout as a .pagx file in the designated directory for easy access.
    - Provides progress messages detailing the export status of each layout.

Usage: Run the tool providing the project path and destination directory to export layouts.

Requirements:
    - ArcGIS Pro with relevant permissions and licenses.
    - Valid paths for the project file and output directory.

Date: July 2024
File: export_all_layouts_into_PAGX.py
Author: github.com/alex6H
"""

import arcpy
import os

def export_layouts_to_pagx(aprx_path, output_directory):

    arcpy.AddMessage("Work in progess... ")

    # Open the current ArcGIS project if non have been specified
    if len(aprx_path)==0:
        arcpy.AddMessage("Current project will be used")
        aprx = arcpy.mp.ArcGISProject("CURRENT")
    else :
        aprx = arcpy.mp.ArcGISProject(aprx_path)

    # List all layouts in the project
    layouts = aprx.listLayouts()

    # Iterate through each layout and export as .pagx file
    for layout in layouts:
        layout_name = layout.name
        output_pagx = os.path.join(output_directory, f'{layout_name}.pagx')
        layout.exportToPAGX(output_pagx)
        arcpy.AddMessage(f'Exported layout {layout_name}')

    # Clean up: close the ArcGIS project
    del aprx

    arcpy.AddMessage("All layouts have been exported successfully. Have a good day!")


if __name__ == "__main__":

    # Get params:
    aprx_path = arcpy.GetParameterAsText(0)
    output_directory = arcpy.GetParameterAsText(1)
    
    # Run function
    export_layouts_to_pagx(aprx_path, output_directory)