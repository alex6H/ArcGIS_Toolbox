# ArcGIS Toolbox

Welcome to the Tools Box repository! This collection of tools is designed to simplify and streamline various data management tasks.
- Incremental ID Generator
- Random Unique ID Generator
- Import All Project's Shapefiles In The GDB
- Reproject GDB
- Unused Feature Class Finder V2

This repository is under construction. Do not hesite to raise any issue.


### ID Generator
#### Incremental ID Generator

Generate sequential IDs effortlessly. Ideal for creating ordered identifiers.

Features:
- Adds sequential IDs to a column in an ArcGIS layer.
- Allows customization of the starting value and interval for the IDs.
- Optionally pads IDs with leading zeroes for consistent length.
- Supports adding a prefix and/or suffix to the IDs.
- Automatically adds the specified column to the input layer if it doesn't exist.

Parameters:

- Input Layer: The ArcGIS layer or table where the IDs will be added.
- Starting Value : The initial value for the sequential IDs.
- Interval : The step increment between each sequential ID.
- Column Name: The name of the column to populate with the sequential IDs.
- Pad Zeroes: Boolean option to pad IDs with leading zeroes.
- Prefix: Optional prefix to prepend to each ID.
- Suffix: Optional suffix to append to each ID.

![image](https://github.com/user-attachments/assets/9e88eeb3-47e5-43c0-9bac-ea2b6eaae906)

#### Random Unique ID Generator

Feature:
This tool adds a unique random ID to a specified field in an ArcGIS feature class. It generates IDs based on configurable options and ensures that each ID is unique within the feature class.

Parameters:
- Input Layer or Feature class (str): Full path to the feature class.
- Name of the new ID field (str): Name of the field to add the ID to.
- Include Numbers (bool): Include numbers in the ID (default=True).
- Include Letters (bool): Include letters in the ID (default=True).
- Letter Case (str): Case of letters to use ('upper', 'lower', 'mixed') (default='mixed').
- Maximum Length (int): Maximum length of the ID (default=10).

![image](https://github.com/user-attachments/assets/e5045aca-e624-4166-b509-c7b3d0e00cfb)

### Data management
#### Import All Project's Shapefiles In The GDB

Easily import all shapefiles of a project into a Geodatabase (GDB). All shapefile will be imported in EPSG 3857

Feature:
This tool manages shapefiles within an ArcGIS Pro project by:

- Extracting file paths of feature layers.
- Importing shapefiles into a specified geodatabase and feature dataset.
- Reconnecting feature layers to the imported feature classes in the geodatabase.

Parameters:

- Geodatabase Path  (str): Path to the target File Geodatabase (GDB).
- Reconnect Feature Classes  (str): Flag to indicate whether to reconnect feature classes to the layers ('true' or 'false').

![image](https://github.com/user-attachments/assets/4d6876b7-927e-4095-b869-ec6dcb59fa54)

#### Reproject GDB

Reproject an entire Geodatabase to a new coordinate system with ease.

Feature:

- Retrieves all feature classes and feature datasets from a specified geodatabase.
- Reprojects feature classes to a new spatial reference and saves them in a new geodatabase.
- Optionally reconnects feature classes in an ArcGIS Pro project to the new geodatabase.

Parameters:
- Geodatabase Path (str): Path to the original geodatabase containing the feature classes and datasets to be reprojected.
- New Geodatabase Path (str): Path where the new geodatabase will be created to store reprojected feature classes. The default name will be the same as input GDB + "_Reprojected"
- Reconnect to New GDB (str): Flag to indicate whether to reconnect feature classes in the ArcGIS Pro project to the new geodatabase ('true' or 'false').
- EPSG (str): Spatial reference (coordinate system) for reprojecting the feature classes.

![image](https://github.com/user-attachments/assets/b7eaab9a-6e94-40b4-bfa1-8a91bf005a67)

#### Unused Feature Class Finder V2

Identify and manage unused feature classes within your Geodatabase to optimize storage and organization.

Feature:
This tool identifies feature classes in specified geodatabases that are not used in any ArcGIS project maps. It compares the feature classes listed in the geodatabases against those referenced in the provided ArcGIS project files.

Parameters:

- Input Geodatabase(s)  (list of str): A list of paths to geodatabases. 
- Input Project(s)  (list of str): A list of paths to ArcGIS project (.aprx) files. Leave empty to use the current project

![image](https://github.com/user-attachments/assets/45eba596-fff1-4237-8432-85c951b64de4)

Returns:

- list of unsued feature class. You will need to open "view details"

![image](https://github.com/user-attachments/assets/43066d53-a019-4831-87a0-fd4b7293c96b)
