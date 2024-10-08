# ArcGIS Toolbox

Welcome to the Tools Box repository! 

This collection of tools in [**_Extra_tools.tbx_**](https://github.com/alex6H/ArcGIS_Toolbox/blob/main/Extra_tools.tbx) is designed to simplify and streamline various data management tasks.
- [1. Data management](#1-data-management)
	- [Import All Project's Shapefiles In The GDB](#import-all-projects-shapefiles-in-the-gdb)
	- [Reproject GDB](#reproject-gdb)
- [2. Large Language Model (LLM)](#2-large-language-model-llm)
	- [Data Processing With Online LLM](#data-processing-with-online-llm)
- [3. Finder](#3-finder)
	- [Unused Feature Class Finder V2](#unused-feature-class-finder-v2)
 	- [Layout Finder](#layout-finder)
	- [Data Finder with AOI](#data-finder-with-aoi)
- [4. ID Generator](#4-id-generator)
	- [Incremental ID Generator](#incremental-id-generator)
	- [Random Unique ID Generator](#random-unique-id-generator)
- [5. Export](#1-data-management)
	- [Export All Layouts into .PAGX](#export-all-layouts-into-pagx)
- [License](#1-data-management)

This repository is under construction. Do not hesite to raise any issue.

# 1. Data management
## Import All Project's Shapefiles In The GDB

Easily import all shapefiles of a project into a Geodatabase (GDB). All shapefile will be imported in EPSG 3857.

**Feature:**

This tool manages shapefiles within an ArcGIS Pro project by:

- Extracting file paths of feature layers.
- Importing shapefiles into a specified geodatabase and feature dataset.
- Reconnecting feature layers to the imported feature classes in the geodatabase.

Please note that if you click "View details" you will have access to the logs.

**Parameters:**
- Geodatabase Path  (str): Path to the target File Geodatabase (GDB).
- Reconnect Feature Classes  (str): Flag to indicate whether to reconnect feature classes to the layers ('true' or 'false').

![image](https://github.com/user-attachments/assets/4d6876b7-927e-4095-b869-ec6dcb59fa54)

## Reproject GDB

Reproject an entire Geodatabase to a new coordinate system with ease.

**Feature:**
- Retrieves all feature classes and feature datasets from a specified geodatabase.
- Reprojects feature classes to a new spatial reference and saves them in a new geodatabase.
- Optionally reconnects feature classes in an ArcGIS Pro project to the new geodatabase.

Note that the new GDB will not displays automaticaly in your ArcGIS Pro project. You will have to import it manually.

**Parameters:**
- Geodatabase Path (str): Path to the original geodatabase containing the feature classes and datasets to be reprojected.
- New Geodatabase Path (str): Path where the new geodatabase will be created to store reprojected feature classes. The default name will be the same as input GDB + "_Reprojected"
- Reconnect to New GDB (str): Flag to indicate whether to reconnect feature classes in the ArcGIS Pro project to the new geodatabase ('true' or 'false').
- EPSG (str): Spatial reference (coordinate system) for reprojecting the feature classes.

![image](https://github.com/user-attachments/assets/b7eaab9a-6e94-40b4-bfa1-8a91bf005a67)

# 2. Large Language Model (LLM)
## Data Processing With Online LLM

**Feature:**

This tool is designed to enhance your geospatial data processing capabilities by integrating a Large Language Model (LLM) like ChatGPT into your ArcGIS workflows. It allows you to extract and/or transform attribute data from a specified feature class, process that data using advanced language models, and store the results in a new field within the same feature class. The tool leverages the [DuckDuckGo search API ](https://github.com/deedy5/duckduckgo_search)
 to facilitate communication with the LLM, enabling you to perform tasks such as summarization, data extraction, and more.

The DuckDuckGo Search API eliminates the need for a local setup of the LLM, but it does expose your data to external sources. Additionally, the DuckDuckGo Search API may temporarily block you if you exceed the allowed number of requests

**Before running the tool:**

The DuckDuckGo Search API is an external library that needs to be installed. However, the default ArcGIS Python environment cannot be modified. Therefore, we will need to clone the original environment to install the DuckDuckGo Search API. To copy the Python environment, navigate to _Project > Package Manager_ and click on the wheel icon on the right.
![image](https://github.com/user-attachments/assets/4c01750c-bd21-4315-b66d-c32b64013c6f)
Then clone the default _arcgispro-py3_ environnement, then switch to your new environment and restart Arcgis Pro.

The first run of the tool will install DuckDuckGo Search API (internet connexion needed).

**Parameters:**
- Input Layer or Feature Class: Path to the input feature class or layer. This is the main dataset you will be working on.
  - Example: C:\MyGDB.gdb\MyFeatureClass
- Input attribute: Name of the field containing the attribute data to be processed. This is the source of the text data you want to analyze and send to the LLM.
  - Example: description
- LLM output column: Name of the new field where results will be stored. This field will be added to your feature class to store the LLM results.
  - Example: processed_text
- Task for the LLM: Description of the task to send to the LLM. This should specify what you want the LLM to do with the text data (e.g., summarize, extract specific info).
  - Example: Extract the main location from the following description.
- Model: The LLM model to use. Specify which model to employ for processing the text. With the DuckDuckGo search API these models are available:
  - ChatGpt 4o-mini (from OpenAI).
  - Claude-3-haiku (from Antropic)
  - Llama-3.1 -70b (from Meta)
  - Mixtral-8x7b (from Mistral)
- Delay in second: Time to wait between processing records (useful for rate limiting). This helps to avoid overloading the API with too many requests at once.
  - Example: 1.0 (waits 1 second between processing each record)
- Force update of the duckduckgo_search library : Check this option to force the tool to update the duckduckgo_search package to the latest version, even if it is already installed.Restart of Arcgis will be requierd!

Please note that, behind the scenes, the tool specifies the LLM with additional instructions: 'Show the answer between brackets; respond ONLY with the answer!' This is designed to prevent the LLM from being overly verbose, ensuring that the tool can extract the correct information. The tool then extracts the first element within the brackets from the LLM answer and sends it to the attribute table.

**Example :**
 
![image](https://github.com/user-attachments/assets/9548dfd5-6481-45e9-aab1-3332ae7ad1aa)

Output will be

![image](https://github.com/user-attachments/assets/06cb0082-c751-4896-818b-1d9404227554)

# 3. Finder
## Unused Feature Class Finder V2

Identify and manage unused feature classes within your Geodatabase to optimize storage and organization.

**Feature:**

This tool identifies feature classes in specified geodatabases that are not used in any specified ArcGIS project maps. It compares the feature classes listed in the geodatabases against those referenced in the provided ArcGIS project files.

**Parameters:**
- Input Geodatabase(s)  (list of str): A list of paths to geodatabases. 
- Input Project(s)  (list of str): A list of paths to ArcGIS project (.aprx) files. Leave empty to use the current project

![image](https://github.com/user-attachments/assets/45eba596-fff1-4237-8432-85c951b64de4)

Note that you will need to open "view details" at the bottom of the tool to see the list of unused feature classes in the logs.
![image](https://github.com/user-attachments/assets/43066d53-a019-4831-87a0-fd4b7293c96b)

## Layout Finder

**Feature:**

This tool helps you search through all .aprx files in a specified folder and subfolders to find any layouts whose names contain a specific substring. It identifies and lists the project files and corresponding layout names that match your search criteria.

**Parameters**

- Root Folder Path :
	- Specify the path to the folder where the search will be conducted. The tool will recursively search through this folder and its subdirectories for .aprx files.
- Layout Name to search for : 
	- Enter a substring (part of the layout name) or the full name to search for. The tool will look for layouts in each APRX file whose names contain this substring, regardless of the case (CaSE InSeNsItIve).

 ![image](https://github.com/user-attachments/assets/0d135afb-2573-44cc-a1ca-f01caf6209d4)

Results will be in the "View" Details". 

## Data Finder with AOI

**Feature:**

This tool searches through geodatabases, shapefiles, and GPX files within a specified folder and its subfolders to identify features that match a defined spatial relationship (e.g., INTERSECT, WITHIN) with a given Area of Interest (AOI). It also allows filtering by geometry type (points, lines, polygons).

If you need to determine whether relevant data exists within a specific AOI, this tool automates the search process across multiple files and folders.

**Parameters**

- Input Path: Specify one or multiple folders containing your geospatial data.
- Area of Interest (AOI): Provide the AOI feature class (POLYGON)
- Spatial Relationship: Choose the spatial relationship type (e.g., INTERSECT, WITHIN,...).
- Data Types:
	- Geodatabases (.gdb): Check to include.
	- Shapefiles (.shp): Check to include. (Locked files are skipped and raise a warning)
	- GPX Files (.gpx): Check to include. (GPX is always considered as a POINTS layer)
- Geometry Filters:
	- Points: Check to include.
	- Lines: Check to include.
	- Polygons: Check to include.

![image](https://github.com/user-attachments/assets/9e62ea86-63f4-48b6-aa4f-6bec158e4086)

Results are in the log "View details"

# 4. ID Generator
## Incremental ID Generator

This tool generates and populates a new column (new_ID) in an attribute table of a specified input layer with unique incremental IDs. These IDs can be customized with prefixes, suffixes, and zero padding, depending on user preferences. Ideal for creating ordered identifiers.

**Features:**
- Adds sequential IDs to a column in an ArcGIS layer.
- Allows customization of the starting value and interval for the IDs.
- Optionally pads IDs with leading zeroes for consistent length.
- Supports adding a prefix and/or suffix to the IDs.
- Automatically adds the specified column to the input layer if it doesn't exist.

**Parameters:**

The tool takes several parameters to customize the unique IDs it generates and populates in the attribute table. Here's an explanation of each parameter:
- Input Layer : This parameter specifies the input feature class where the new column will be added and populated with unique IDs.
- Start Value : This is the initial value for the ID sequence. The first ID will start from this number.
- Interval : This parameter defines the increment between successive IDs. 
For instance, if Start Value is 1 and Interval is 2, the IDs will be 1, 3, 5, etc.
- Column Name : The name of the new column where the unique IDs will be stored. The tool checks if this column already exists and raises a warning before stopping if it does to not erase data.
- Pad Zeroes : A boolean parameter that determines whether the IDs should be padded with leading zeros. This ensures all IDs have the same length. It is particulary useful when dealing with number in string format.
	- Example: If there are 100 records and the IDs need to be padded with zeros, the generated IDs will be 001, 002, 003, ..., 100 instead of 1, 2, 3, ..., 100.
- Prefix : An optional text string to be added before each unique ID. This can help in distinguishing IDs from different sources or datasets.
	- Example: If the prefix is ID_, the generated IDs will be ID_001, ID_002, ID_003, ..., ID_100.
- Suffix : An optional text string to be added after each unique ID, similar to the prefix.
  - Example: If the suffix is _A, the generated IDs will be 001_A, 002_A, 003_A, ..., 100_A.

**Note that :**
- If no prefix, suffix and padding are used, the data type will be integer (long)
- Else, data type will be string (Text)

![image](https://github.com/user-attachments/assets/2a94b55d-860a-4736-89f4-c1ad88120752)

## Random Unique ID Generator

**Feature:**
This tool create a column with unique random ID in the attribute table of a GDB feature class. The ID can include numbers, letters (upper, lower, or mixed case), and can have a specified maximum length.

**Parameters:**
- Input Layer or Feature class : This parameter specifies the input feature class where the new column will be added and populated with unique IDs.
- Name of the new column : Name of the field where the unique ID will be added.
- Include Number: A boolean parameter that determines whether numbers (0 to 9) should be included in the unique ID.
- Include Letters : A boolean parameter that determines whether letters (A to Z) should be included in the unique ID.
- Letter Case : Specifies the case of the letters used in the unique ID. Options are 'upper', 'lower', or 'mixed'. Example:
  - 'upper' (to include uppercase letters only, e.g., ABC)
  - 'lower' (to include lowercase letters only, e.g., abc)
  - 'mixed' (to include both upper and lower case letters, e.g., aBc)
- Maximum Length: Length of the unique ID. Example:
  - 5 (to generate IDs up to 5 characters long, e.g., aB3dE)
  - 8 (to generate IDs up to 8 characters long, e.g., A1b2C3d4)
  - 10 (to generate IDs up to 10 characters long, e.g., Ab3De4Fg5H)

![image](https://github.com/user-attachments/assets/e5045aca-e624-4166-b509-c7b3d0e00cfb)

# 5. Export
## Export All Layouts into .PAGX
**Feature:**

This script automates the export of all layouts within an ArcGIS Pro project to individual .pagx files. It simplifies the process of extracting layout designs from a project, making it easy to share or reuse layouts in other projects.

**Parameters:**

- APRX Path: The file path to the ArcGIS Pro project (.aprx) from which the layouts will be exported. If left blank, the script will use the currently open project.
- Output directory: The directory where the exported .pagx files will be saved. Each layout will be saved as a separate .pagx file in this location.
- 
![image](https://github.com/user-attachments/assets/a09af96e-dc34-43fd-855a-d8c0e5dd82a1)

# Licence
This work is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License.

You are free to:
- Share: Copy and redistribute the material in any medium or format.
- Adapt: Remix, transform, and build upon the material.

Under the following terms:
- Attribution: You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
- NonCommercial: You may not use the material for commercial purposes.
- Citation: If you republish or modify the material, please include a citation to the original work.

No additional restrictions: You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.

For more details, see the full license at https://creativecommons.org/licenses/by-nc/4.0/.


