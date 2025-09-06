# ArcGIS Toolbox - Extra tools.tbx

![License](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)
![GitHub last commit](https://img.shields.io/github/last-commit/alex6H/ArcGIS_Toolbox)
![GitHub issues](https://img.shields.io/github/issues/alex6H/ArcGIS_Toolbox)
![GitHub stars](https://img.shields.io/github/stars/alex6H/ArcGIS_Toolbox)
![GitHub forks](https://img.shields.io/github/forks/alex6H/ArcGIS_Toolbox)
![ArcGIS Pro](https://img.shields.io/badge/ArcGIS%20Pro-3.x-blue)
![Python](https://img.shields.io/badge/Python-arcgispro--py3-yellow)
![Status](https://img.shields.io/badge/Status-Active%20Development-green)

Welcome to the Tools Box repository, a collection of **custom ArcGIS Pro geoprocessing tools** to make some repetitive actions easier.  
All tools are packaged as an `.atbx` (ArcGIS Pro toolbox) in [**_Extra_tools.atbx_**](https://github.com/alex6H/ArcGIS_Toolbox/blob/main/Extra%20tools.atbx) and leverage Python functionality to streamline data management and automate workflows in both ArcGIS Pro and ArcGIS Online/Portal.

> **Status:** Repository under active development. Feedback and contributions welcome!

## Content
- [1. Data management](#1-data-management)
	- [Import All Project's Shapefiles In The GDB](#import-all-projects-shapefiles-in-the-gdb)
	- [Reproject GDB](#reproject-gdb)
- [2. Large Language Model (LLM)](#2-large-language-model-llm)
	- [Data Processing With Online LLM](#data-processing-with-online-llm)
- [3. Finder](#3-finder)
	- [Unused Feature Class Finder](#unused-feature-class-finder)
 	- [Layout Finder](#layout-finder)
	- [Data Finder with AOI](#data-finder-with-aoi)
- [4. ID Generator](#4-id-generator)
	- [Incremental ID Generator](#incremental-id-generator)
	- [Random Unique ID Generator](#random-unique-id-generator)
- [5. Export](#5-export)
	- [Export All Layouts into .PAGX](#export-all-layouts-into-pagx)
 	- [Export All Layouts into .MAPX](#export-all-layouts-into-mapx)
- [6. AGOL - PORTAL](#6-agol---portal)
	- [Item group membership checker](#item-group-membership-checker)
	- [Copy layers between web maps](#copy-layers-between-web-maps)
 	- [Copy layer symbology](#copy-layer-symbology)
 	- [Copy Bookmarks Between WebMaps](#copy-bookmarks-between-web-maps)
 - [Contact & Issues](#contact--issues)
- [Licence](#licence)

## Keywords
`ArcGIS Pro` • `Python` • `Geoprocessing` • `Spatial Analysis` • `Data Management` • `Automation` • `GIS Tools` • `Geodatabase` • `AGOL` • `Portal` • `ArcPy` • `Workflow` • `Geospatial` • `ESRI`

## Requirements
- **ArcGIS Pro 3.x** with the default Python environment (`arcgispro-py3`)
- The tools have been tested with Arcgis Pro 3.3.5
- For some tools, ability to clone the ArcGIS environment to install extra packages

## Installation

1. **Download the Toolbox**
   - [Download Extra_tools.atbx](https://github.com/alex6H/ArcGIS_Toolbox/blob/main/Extra%20tools.atbx) from GitHub.

2. **Add to ArcGIS Pro**
   - Open ArcGIS Pro.
   - Go to `Catalog` ➔ Right-click `Toolboxes` ➔ `Add Toolbox...`
   - Select `Extra_tools.atbx`.

3. **(Optional) Clone Python Environment for Extra Packages**
   - Go to `Project > Package Manager` in ArcGIS Pro.
   - Click the settings wheel ➔ Clone `arcgispro-py3`.
   - Switch to your new environment and restart ArcGIS Pro.

# 1. Data management
## Import All Project's shapefiles in the GDB

Easily import all shapefiles of a project into a Geodatabase (GDB). All shapefile will be imported in EPSG 3857.

**Feature:**

This tool manages shapefiles within an ArcGIS Pro project by:

- Extracting file paths of feature layers.
- Importing shapefiles into a specified geodatabase and feature dataset.
- Reconnecting feature layers to the imported feature classes in the geodatabase.

Please note that if you click "View details" you will have access to the logs.

**Parameters:**

| Parameter                | Description                                                             | Required | Example                                 |
|--------------------------|-------------------------------------------------------------------------|----------|-----------------------------------------|
| Geodatabase Path         | Path to the target File Geodatabase (GDB).                              | Yes      | `C:\Data\MyDatabase.gdb`                |
| Reconnect Feature Classes| Flag to indicate whether to reconnect feature classes to the layers.     | Yes      | `true` or `false`                       |

![image](https://github.com/user-attachments/assets/4d6876b7-927e-4095-b869-ec6dcb59fa54)

## Reproject GDB

Reproject an entire Geodatabase to a new coordinate system with ease.

**Feature:**
- Retrieves all feature classes and feature datasets from a specified geodatabase.
- Reprojects feature classes to a new spatial reference and saves them in a new geodatabase.
- Optionally reconnects feature classes in an ArcGIS Pro project to the new geodatabase.

Note that the new GDB will not displays automatically in your ArcGIS Pro project. You will have to import it manually.

**Parameters:**

| Parameter                | Description                                                                                              | Required | Example                                         |
|--------------------------|----------------------------------------------------------------------------------------------------------|----------|-------------------------------------------------|
| Geodatabase Path         | Path to the original geodatabase containing the feature classes and datasets to be reprojected.          | Yes      | `C:\Data\Source.gdb`                            |
| New Geodatabase Path     | Path where the new geodatabase will be created to store reprojected feature classes.                     | Yes      | `C:\Data\Source_Reprojected.gdb`                |
| Reconnect to New GDB     | Flag to indicate whether to reconnect feature classes in the ArcGIS Pro project to the new geodatabase.  | Yes      | `true` or `false`                               |
| EPSG                     | Spatial reference (coordinate system) for reprojecting the feature classes.                              | Yes      | `4326`, `3857`, `EPSG:32633`                    |

![image](https://github.com/user-attachments/assets/b7eaab9a-6e94-40b4-bfa1-8a91bf005a67)


# 2. Large Language Model (LLM)
## Data processing with online LLM

**Feature:**

This tool is designed to enhance data processing capabilities by integrating a Large Language Model (LLM) like ChatGPT into your ArcGIS workflows. It allows you to extract and/or transform attribute data from a specified feature class, process that data using advanced language models, and store the results in a new field within the same feature class. The tool leverages the [DuckDuckGo search API ](https://github.com/deedy5/duckduckgo_search)
 to facilitate communication with the LLM, enabling to perform tasks such as summarization, data extraction, and more.

The DuckDuckGo Search API eliminates the need for a local setup of the LLM, but it does expose your data to external sources. Additionally, the DuckDuckGo Search API may temporarily block you if you exceed the allowed number of requests

**Before running the tool:**

The DuckDuckGo Search API is an external library that needs to be installed. However, the default ArcGIS Python environment cannot be modified. Therefore, we will need to clone the original environment to install the DuckDuckGo Search API. To copy the Python environment, navigate to _Project > Package Manager_ and click on the wheel icon on the right.
![image](https://github.com/user-attachments/assets/4c01750c-bd21-4315-b66d-c32b64013c6f)
Then clone the default _arcgispro-py3_ environnement, then switch to your new environment and restart Arcgis Pro.

The first run of the tool will install DuckDuckGo Search API (internet connection needed).

**Parameters:**

| Parameter                           | Description                                                                                                                    | Required | Example                        |
|--------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|----------|--------------------------------|
| Input Layer or Feature Class         | Path to the input feature class or layer. This is the main dataset you will be working on.                                     | Yes      | C:\MyGDB.gdb\MyFeatureClass    |
| Input Attribute                      | Name of the field containing the attribute data to be processed. This is the source of the text data for the LLM.              | Yes      | description                    |
| LLM Output Column                    | Name of the new field where results will be stored. This field will be added to your feature class to store the LLM results.   | Yes      | processed_text                 |
| Task for the LLM                     | Description of the task to send to the LLM (e.g., summarize, extract specific info).                                           | Yes      | Extract the main location from the following description. |
| Model                                | The LLM model to use. Specify which model to employ for processing the text. Available models (via DuckDuckGo search API):     | Yes      | ChatGpt 4o-mini, Claude-3-haiku, Llama-3.1-70b, Mixtral-8x7b |
| Delay (seconds)                      | Time to wait between processing records (for rate limiting; helps avoid API overload).                                         | No       | 1.0                            |
| Force Update duckduckgo_search Library| Check this option to force update the duckduckgo_search package to the latest version, even if already installed. ArcGIS restart required. | No       | true / false                   |

Please note that, behind the scenes, the tool specifies the LLM with additional instructions: 'Show the answer between brackets; respond ONLY with the answer!' This is designed to prevent the LLM from being overly verbose, ensuring that the tool can extract the correct information. The tool then extracts the first element within the brackets from the LLM answer and sends it to the attribute table.

**Example :**
 
![image](https://github.com/user-attachments/assets/9548dfd5-6481-45e9-aab1-3332ae7ad1aa)

Output will be

![image](https://github.com/user-attachments/assets/06cb0082-c751-4896-818b-1d9404227554)


# 3. Finder
## Unused feature class finder

Identify and manage unused feature classes within your Geodatabase to optimize storage and organization.

**Feature:**

This tool identifies feature classes in specified geodatabases that are not used in any specified ArcGIS project maps. It compares the feature classes listed in the geodatabases against those referenced in the provided ArcGIS project files.

**Parameters:**

| Parameter             | Type        | Description                                                                                                         | Required | Example                                                        |
|-----------------------|-------------|---------------------------------------------------------------------------------------------------------------------|----------|----------------------------------------------------------------|
| Input Geodatabase(s)  | list of str | A list of file paths to geodatabases. Each path should be a string representing the full location of a GDB file.    | Yes      | "C:/Data/mydata.gdb"              |
| Input Project(s)      | list of str | A list of file paths to ArcGIS project (.aprx) files. Leave empty to use the currently open ArcGIS project.         | No       | "C:/Projects/project1.aprx"         |

![image](https://github.com/user-attachments/assets/45eba596-fff1-4237-8432-85c951b64de4)

Note that you will need to open "view details" at the bottom of the tool to see the list of unused feature classes in the logs.
![image](https://github.com/user-attachments/assets/43066d53-a019-4831-87a0-fd4b7293c96b)

## Layout Finder

**Feature:**

This tool helps you search through all .aprx files in a specified folder and subfolders to find any layouts whose names contain a specific substring. It identifies and lists the project files and corresponding layout names that match your search criteria.

**Parameters**

| Parameter                 | Description                                                                                                              | Required | Example                      |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------|----------|------------------------------|
| Root Folder Path          | Path to the folder where the search will be conducted. The tool will recursively search for `.aprx` files in subfolders. | Yes      | C:\Projects\GIS_Files        |
| Layout Name to Search For | Substring or full layout name to look for (case insensitive). Searches for layouts in each `.aprx` whose name matches.   | Yes      | "mymap_AOL_12Dec2024"      |

 ![image](https://github.com/user-attachments/assets/0d135afb-2573-44cc-a1ca-f01caf6209d4)

Results will be in the "View" Details". 

## Data finder with AOI

**Feature:**

This tool searches through geodatabases, shapefiles, and GPX files within a specified folder and its subfolders to identify features that match a defined spatial relationship (e.g., INTERSECT, WITHIN) with a given Area of Interest (AOI). It also allows filtering by geometry type (points, lines, polygons).

If you need to determine whether relevant data exists within a specific AOI, this tool automates the search process across multiple files and folders.

**Parameters**

### Parameters

| Parameter            | Type                | Description                                                                                                  | Required | Example(s)                             |
|----------------------|---------------------|--------------------------------------------------------------------------------------------------------------|----------|-----------------------------------------|
| Input Path           | list of str         | One or more folder paths containing geospatial data.                                                         | Yes      | ["C:/GIS/Data", "D:/Projects/Spatial"] |
| Area of Interest     | str (feature class) | Path to the AOI feature class (must be a POLYGON).                                                          | Yes      | "C:/GIS/Boundaries/aoi_polygon.shp"    |
| Spatial Relationship | str                 | Spatial relationship type to apply (e.g., INTERSECT, WITHIN, CONTAINS, TOUCHES, OVERLAPS, CROSSES, etc.).   | Yes      | "INTERSECT"                            |
| Geodatabases         | bool                | Include Geodatabases (.gdb) in the search.                                                                   | No       | True                                   |
| Shapefiles           | bool                | Include Shapefiles (.shp) in the search. (Locked files are skipped with a warning.)                          | No       | True                                   |
| GPX                  | bool                | Include GPX files (.gpx) in the search. (Always treated as POINTS layer.)                                    | No       | True                                   |
| Points               | bool                | Include POINT geometry types.                                                                                | Yes      | True                                   |
| Lines                | bool                | Include LINE geometry types.                                                                                 | Yes      | True                                   |
| Polygons             | bool                | Include POLYGON geometry types.                                                                              | Yes      | True                                   |

![image](https://github.com/user-attachments/assets/9e62ea86-63f4-48b6-aa4f-6bec158e4086)

Results are in the log "View details"


# 4. ID Generator
## Incremental ID generator

This tool generates and populates a new column (new_ID) in an attribute table of a specified input layer with unique incremental IDs. These IDs can be customized with prefixes, suffixes, and zero padding, depending on user preferences. Ideal for creating ordered identifiers.

**Features:**

- Adds sequential IDs to a column in an ArcGIS layer.
- Allows customization of the starting value and interval for the IDs.
- Optionally pads IDs with leading zeroes for consistent length.
- Supports adding a prefix and/or suffix to the IDs.
- Automatically adds the specified column to the input layer if it doesn't exist.

**Parameters:**

| Parameter     | Type          | Description                                                                                                                     | Required | Example                |
|---------------|--------------|---------------------------------------------------------------------------------------------------------------------------------|----------|------------------------|
| Input Layer   | str           | Path to the input feature class where the new column will be added and populated with unique IDs.                               | Yes      | "C:/GIS/Data/parcels.shp" |
| Start Value   | int           | Initial value for the ID sequence. The first ID will start from this number.                                                    | Yes      | 1                      |
| Interval      | int           | Increment between successive IDs.                                                                                              | Yes      | 2                      |
| Column Name   | str           | Name of the new column for unique IDs. If the column exists, the tool raises a warning and stops to prevent overwriting data.  | Yes      | "UniqueID"             |
| Pad Zeroes    | bool          | Whether to pad IDs with leading zeros so all IDs have the same length (useful for string-formatted numbers).                   | Yes      | True                   |
| Prefix        | str (optional)| Optional text to add before each unique ID.                                                                                   | No       | "ID_"                  |
| Suffix        | str (optional)| Optional text to add after each unique ID.                                                                                    | No       | "_A"                   |

**Note that :**
- If no prefix, suffix and padding are used, the data type will be integer (long)
- Else, data type will be string (Text)

![image](https://github.com/user-attachments/assets/2a94b55d-860a-4736-89f4-c1ad88120752)

## Random unique ID generator

**Feature:**

This tool create a column with unique random ID in the attribute table of a GDB feature class. The ID can include numbers, letters (upper, lower, or mixed case), and can have a specified maximum length.

**Parameters:**

| Parameter                | Description                                                                                      | Required | Example                         |
|--------------------------|--------------------------------------------------------------------------------------------------|----------|---------------------------------|
| Input Layer or Feature class | The input feature class where the new column will be added and populated with unique IDs.        | Yes      | `Parcels` or `C:\data\roads.gdb\roads_fc` |
| Name of the new column   | Name of the field where the unique ID will be added.                                             | Yes      | `UniqueID`                      |
| Include Number           | Whether numbers (0-9) should be included in the unique ID.                                       | Yes      | `True` or `False`               |
| Include Letters          | Whether letters (A-Z) should be included in the unique ID.                                       | Yes      | `True` or `False`               |
| Letter Case              | Case of the letters used: 'upper', 'lower', or 'mixed'.                                          | Yes      | `upper`, `lower`, `mixed`       |
| Maximum Length           | Maximum length of the unique ID to generate.                                                     | Yes      | `5`, `8`, `10`                  |

![image](https://github.com/user-attachments/assets/e5045aca-e624-4166-b509-c7b3d0e00cfb)


# 5. Export

## Export all layouts into .PAGX
**Feature:**

This script automates the export of all layouts within an ArcGIS Pro project to individual .pagx files. It simplifies the process of extracting layout designs from a project, making it easy to share or reuse layouts in other projects.

**Parameters:**

- APRX Path: The file path to the ArcGIS Pro project (.aprx) from which the layouts will be exported. If left blank, the script will use the currently open project.
- Output directory: The directory where the exported .pagx files will be saved. Each layout will be saved as a separate .pagx file in this location.

![image](https://github.com/user-attachments/assets/a09af96e-dc34-43fd-855a-d8c0e5dd82a1)

## Export all layouts into .MAPX
**Feature:**

- Exports every map in an ArcGIS Pro project to individual .mapx files.
- Automatically creates filesystem-safe filenames by replacing non-alphanumeric characters with underscores.
- Supports exporting from either a specified .aprx file or the currently open ArcGIS Pro project.
- Provides progress messages and warnings via the ArcGIS Pro geoprocessing messages window.


**Parameters:**

| Parameter        | Description                                                                     | Required | Example                         |
|------------------|---------------------------------------------------------------------------------|----------|---------------------------------|
| APRX Path        | Path to the ArcGIS Pro project (.aprx). If empty, uses the currently open project. | Yes      | `C:\Projects\MyProject.aprx`    |
| Output Directory | Directory where the exported `.mapx` files will be saved.                        | Yes      | `C:\Exports\MapX`               |

**Limitations:**

- Filenames are sanitized: all non-alphanumeric characters in map names are replaced with underscores.
- Does not overwrite existing .mapx files with the same name; existing files may be replaced without warning.


# 6. AGOL - PORTAL
## Item group membership checker

**Feature:**

This tool tries to solve the problem of not being able to add yourself as the owner of an AGOL portal item. If the new owner is not a member of all groups with which the item is shared, AGOL will block the owner change. The new owner must be added to all these groups, or the item must be unshared from those groups. This tool try to automatise this process.

<img width="545" alt="image" src="https://github.com/user-attachments/assets/249a23fe-ed2b-4c04-9d6c-0fad3132ed7d" />

It doesn't work in all cases (see Limitations)!

**What It Does:**

<img width="426" alt="image" src="https://github.com/user-attachments/assets/e3b897bf-6cfc-4a28-aa71-f6592d13d23f" />

- Checks all the groups an ArcGIS item is shared with and verifies if you're a member or owner of these groups.
- Automatically attempts to add your user account to groups you're not already a member of.
- Logs detailed results and provides clear feedback on membership and ownership status.

<img width="574" alt="image" src="https://github.com/user-attachments/assets/bdca9ab2-72bc-4941-9da7-afaca975d342" />

**Parameters:**

| Parameter             | Type                | Description                                                                                                   | Required | Example(s)                         |
|-----------------------|---------------------|---------------------------------------------------------------------------------------------------------------|----------|-------------------------------------|
| ArcGIS Item IDs       | list of str         | One or more ArcGIS item IDs to check or manage.                                                               | Yes      | d1e2f3g4h5i6        |
| Add User to Groups    | bool                | Automatically add yourself to groups you're not currently a member of.                                         | No       | True                                |
| Take Item Ownership   | bool                | Attempt to take ownership of the specified items.                                                             | No       | False                               |

Note that if none of the checkboxes are selected, the logs gives your current user status in each groups

**Limitations:**

- You must have sufficient permissions in at least one shared group to successfully transfer ownership.
- Ownership transfer will fail if any associated group has restricted permissions set to "Group owner and managers" only, rather than "All group members".

<img width="545" alt="image" src="https://github.com/user-attachments/assets/e6849772-333e-4884-ad77-56f089bfe8e8" />

## Copy layers between web maps

**Feature:**
This tool automates the process of copying layers from a source Web Map to one or more target Web Maps in AGOL PORTAL. 
It supports the preservation of :
- Symbology
- Labels
- Popups
- Filters
- Visibility range
- Group layer structures
- etc

**Parameters:**

| Parameter        | Description                                                                                   |
|------------------|-----------------------------------------------------------------------------------------------|
| Source WebMap    | Enter the source web map as the source for the layer(s) to be copy.                           |
| Target WebMaps   | List of target web maps as the destination for the layer(s) to be copy                        |
| Layer Names      | Specify the layer(s) titles to copy from the source map to each target map.                   |

<img width="460" alt="image" src="https://github.com/user-attachments/assets/f40f75f4-903d-43e2-9419-cbf55969e13c" />

Run the script then refresh the webmaps pages.
The AGP log/messages window provide the detailed of what is happening behind the curtains

**Limitations:**

- Ownership Restrictions: You can only view and copy layers between web maps that you own. Web maps not owned by you are inaccessible for these operations.
- Connection Dependency: The tool relies on the current ArcGIS Pro connection to either PORTAL or AGOL. If neither is connected, an error will occur. If you don't see the expected webmap, check the connection and ownership.
- Loading Time: The tool requires time to load as it retrieves web map and layer lists from AGOL or PORTAL based on your selections. Please be patient during this process.

## Copy layer symbology

**Feature:**

- Synchronizes layer symbology and related visual settings from a source web map to one or more target web maps.
- Matches layers by name and data source to ensure accurate symbology transfer.
- Can optionally copy display settings (opacity, visibility, scale, labels) and popup configuration (popupInfo, disablePopup).
- Supports batch processing for multiple target web maps.
- Optional verbose mode for advanced debugging and detailed output.

<img width="526"  alt="image" src="https://github.com/user-attachments/assets/d74dc1f8-1dd6-4cb5-82dc-1e985936c6ac" />

**Parameters:**

| Parameter                | Description                                                           | Required | Example                                      |
|--------------------------|----------------------------------------------------------------------|----------|----------------------------------------------|
| Source Web Map           | Item ID of the source web map to copy symbology from                 | Yes      | `123abc456def789ghi012jkl345mno678pqr`       |
| Target Web Map(s)        | Semicolon-separated list of target web map Item IDs                  | Yes      | `987zyx654wvu321tsr;654zyx321wvu987tsr`      |
| Layer(s) to Copy         | Semicolon-separated list of layer names to synchronize               | Yes      | `Layer1;Layer2`                              |
| Copy Display Settings    | Copy display settings (opacity, visibility, etc.)                    | Optional | Checked/Unchecked                            |
| Copy Popup Settings      | Copy popup settings (popupInfo, disablePopup)                        | Optional | Checked/Unchecked                            |
| Copy symbology and effect| Copy symbology and effect (popupInfo, disablePopup)                  | Optional | Checked/Unchecked                            |
| Verbose Output           | Enable verbose logging (detailed output)                             | Optional | Checked/Unchecked                            |

**Limitations:**

- Layers must match by **name** and **data source** for symbology to be transferred.
- Requires a valid connection to ArcGIS Online or Portal for ArcGIS.
- Target web maps must have edit permissions.

## Copy Bookmarks Between Web Maps

**Feature:**
Copy Bookmarks Between Web Maps is a geoprocessing tool that automates the transfer of all bookmarks from a source web map to one or more target web maps in AGOL or Portal for ArcGIS. The tool ensures each bookmark is uniquely named in the target maps, minimizing manual effort and helping maintain consistent navigation experiences across multiple web maps.

<img width="526"  alt="image" src="https://github.com/user-attachments/assets/5437e701-21cd-426c-b769-2b7ce270b4f4" />

**Parameters:**

| Parameter          | Description                                                      | Required | Example                                         |
|--------------------|------------------------------------------------------------------|----------|-------------------------------------------------|
| Source Web Map     | Source web map iItemID					`                     	| Yes      | a12b34c56d78e90f12a34b56c78d90ef`      |
| Target Web Maps    | List of target web maps in same format   					    | Yes      | f98e76d54c32b10a98e76d54c32b10a9;e12f34g56h78i90j12k34l56m78n90op` |
| Verbose Logging    | Enable detailed logging output                                   | Optional | Checked/Unchecked                               |

**Limitations:**
- Ownership & Permissions: You must own or have edit permissions for all target web maps.
- Connection Dependency: The tool requires an active ArcGIS Pro connection to AGOL or Portal. If not connected, the tool will fail.
- Bookmark Name Conflicts: If a bookmark name already exists in the target, the tool appends an incremental suffix (e.g., _1, _2) to ensure uniqueness.
- No Selective Copy: All bookmarks from the source map are copied; selective copying is not yet supported.
- Web Map Format: Only works with "Web Map" items (not "Web Scene" or other types).

## License

This project is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/).

You are free to:
- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material

Under these terms:
- **Attribution** — Give appropriate credit, link to the license, and indicate changes
- **NonCommercial** — Not for commercial use
- **Citation** — Cite the original work if republished

For full details, see the [license](https://creativecommons.org/licenses/by-nc/4.0/).


## Contact & Issues

- For help, feature requests, or bug reports, open an issue
- Questions or suggestions? Reach out via GitHub or create a discussion
