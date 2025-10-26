"""
Tool Name: Layout Finder Tool with Fuzzy Matching

Summary: This tool searches for layouts across multiple ArcGIS Pro project files (.aprx) using fuzzy string matching, allowing users to locate layouts with approximate name matches based on a defined similarity threshold.

Parameters:
    - Folder Path: Path to the directory containing ARC files (.aprx) for layout search.
    - Search Term: The name or partial name of the layout being searched.
    - Similarity Threshold: Defines how closely a match must resemble the search term (0.0 to 1.0 scale).
    - Verbose: Enable detailed logging to ArcGIS Pro messages.

Key Features:
    - Utilizes fuzzy matching to identify layouts across multiple projects.
    - Supports configurable similarity cutoff for flexible search results.
    - Generates a detailed report on located layouts with similarity scores to aid in user analysis.

Usage: Provide the folder and terms to search layouts across multiple APRX files using fuzzy logic.

Requirements:
    - ArcGIS Pro with relevant licenses and access permissions.
    - Valid and accessible folder path containing ARC files (.aprx).

Date: July 2024
File: layout_finder.py
Author: github.com/alex6H
"""
import arcpy
from difflib import get_close_matches
from typing import List, Tuple, Dict

def validate_folder(folder_path: str) -> str:
    """
    Validate folder path exists.
    
    Args:
        folder_path: Path to folder containing APRX files
        
    Returns:
        Validated folder path
        
    Raises:
        ValueError: If folder doesn't exist
    """
    if not os.path.exists(folder_path):
        raise ValueError(f"Folder not found: {folder_path}")
    
    if not os.path.isdir(folder_path):
        raise ValueError(f"Path is not a folder: {folder_path}")
    
    return folder_path


def check_similarity(layout_name: str, search_term: str, cutoff: float) -> Tuple[bool, float]:
    """
    Check if search term matches layout name using fuzzy matching.
    
    Args:
        layout_name: Layout name to check
        search_term: Search term to match
        cutoff: Similarity threshold (0.0 to 1.0)
        
    Returns:
        Tuple of (is_match, similarity_score)
    """
    layout_lower = layout_name.lower()
    search_lower = search_term.lower()
    
    # Generate all substrings from layout name
    substrings = [layout_lower[i:j] for i in range(len(layout_lower)) 
                  for j in range(i + 1, len(layout_lower) + 1)]
    
    # Find close matches
    matches = get_close_matches(search_lower, substrings, n=1, cutoff=cutoff)
    
    if matches:
        # Calculate similarity score
        from difflib import SequenceMatcher
        best_match = matches[0]
        similarity = SequenceMatcher(None, search_lower, best_match).ratio()
        return True, similarity
    
    return False, 0.0


def collect_aprx_files(folder_path: str, verbose: bool) -> List[str]:
    """
    Collect all APRX files in folder and subfolders.
    
    Args:
        folder_path: Root folder to search
        verbose: Enable detailed logging
        
    Returns:
        List of APRX file paths
    """
    aprx_files = []
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.aprx'):
                aprx_files.append(os.path.join(root, file))
    
    arcpy.AddMessage(f"Found {len(aprx_files)} APRX file(s) to scan in folder '{folder_path}'")
    
    if verbose and aprx_files:
        arcpy.AddMessage("\nAPRX files found:")
        for aprx in aprx_files:
            arcpy.AddMessage(f"  • {os.path.basename(aprx)}")
    
    return aprx_files


def search_layouts_in_aprx(aprx_path: str, search_term: str, cutoff: float, 
                           verbose: bool) -> Tuple[List[Tuple[str, float]], float, int]:
    """
    Search for matching layouts in a single APRX file.
    
    Args:
        aprx_path: Path to APRX file
        search_term: Search term to match
        cutoff: Similarity threshold
        verbose: Enable detailed logging
        
    Returns:
        Tuple of (matching_layouts list, processing_time, total_layouts)
    """
    start_time = time.time()
    matching_layouts = []
    total_layouts = 0
    
    try:
        aprx = arcpy.mp.ArcGISProject(aprx_path)
        layouts = aprx.listLayouts()
        total_layouts = len(layouts)
        
        if verbose:
            arcpy.AddMessage(f"\n  Scanning {total_layouts} layout(s):")
        
        for layout in layouts:
            is_match, similarity = check_similarity(layout.name, search_term, cutoff)
            
            if verbose:
                if is_match:
                    arcpy.AddMessage(f"    ✓ {layout.name} ({similarity*100:.1f}% match)")
                else:
                    arcpy.AddMessage(f"    ✗ {layout.name}")
            
            if is_match:
                matching_layouts.append((layout.name, similarity))
        
        del aprx
        
    except IOError as e:
        arcpy.AddWarning(f"  ⚠ Skipped (file locked or in use): {os.path.basename(aprx_path)}")
    except Exception as e:
        arcpy.AddWarning(f"  ⚠ Failed to open: {os.path.basename(aprx_path)} - {str(e)}")
    
    processing_time = time.time() - start_time
    return matching_layouts, processing_time, total_layouts


def search_all_aprx_files(aprx_files: List[str], search_term: str, cutoff: float, 
                          verbose: bool) -> Dict[str, List[Tuple[str, float]]]:
    """
    Search for layouts across all APRX files.
    
    Args:
        aprx_files: List of APRX file paths
        search_term: Search term to match
        cutoff: Similarity threshold
        verbose: Enable detailed logging
        
    Returns:
        Dictionary mapping APRX paths to matching layouts with scores
    """
    results = {}
    total_files = len(aprx_files)
    
    arcpy.SetProgressor("step", "Scanning APRX files...", 0, total_files, 1)
    
    for index, aprx_path in enumerate(aprx_files):
        #arcpy.AddMessage("_" * 80)
        arcpy.AddMessage(f"[{index+1}/{total_files}] {os.path.basename(aprx_path)}")
        
        matching_layouts, proc_time, total_layouts = search_layouts_in_aprx(
            aprx_path, search_term, cutoff, verbose
        )
        
        if matching_layouts:
            results[aprx_path] = matching_layouts
            if not verbose:
                arcpy.AddMessage(f"  → {len(matching_layouts)} matching layout(s) found")
        else:
            if not verbose:
                arcpy.AddMessage(f"  → No matches found")
        
        if verbose:
            arcpy.AddMessage(f"  Processing time: {proc_time:.2f}s")
        
        arcpy.SetProgressorPosition(index + 1)
    
    arcpy.ResetProgressor()
    return results


def report_results(results: Dict[str, List[Tuple[str, float]]], search_term: str, 
                  cutoff: float) -> None:
    """
    Display formatted search results.
    
    Args:
        results: Dictionary of APRX paths to matching layouts
        search_term: Search term used
        cutoff: Similarity threshold used
    """
    arcpy.AddMessage("\n" + "=" * 80)
    arcpy.AddMessage("LAYOUT SEARCH RESULTS")
    arcpy.AddMessage("=" * 80)
    
    if not results:
        arcpy.AddMessage("\n✗ No matching layouts found")
        arcpy.AddMessage("=" * 80)
        return
    
    total_matches = sum(len(layouts) for layouts in results.values())
    
    arcpy.AddMessage(f"\n✓ MATCHES FOUND: {total_matches} layout(s) in {len(results)} APRX file(s)")
    arcpy.AddMessage("-" * 80)
    
    for aprx_path in sorted(results.keys()):
        layouts = results[aprx_path]
        arcpy.AddMessage(f"\n✅ {os.path.basename(aprx_path)}")
        arcpy.AddMessage(f"   Path: {aprx_path}")
        # Sort by similarity score (highest first)
        sorted_layouts = sorted(layouts, key=lambda x: x[1], reverse=True)
        
        for layout_name, similarity in sorted_layouts:
            arcpy.AddMessage(f"   → {layout_name} ({similarity*100:.1f}% match)")
    
if __name__ == "__main__":
    try:
        # Get parameters
        folder_path = arcpy.GetParameterAsText(0)
        search_term = arcpy.GetParameterAsText(1)
        cutoff = arcpy.GetParameter(2)  # Long
        verbose = arcpy.GetParameter(3)  # Boolean
        
        # Convert cutoff from percentage to decimal
        cutoff = cutoff/100

        # Validate inputs
        if not search_term or search_term.strip() == "":
            arcpy.AddError("Search term cannot be empty")

        folder_path = validate_folder(folder_path)
        
        arcpy.AddMessage("Starting layout search...")
        arcpy.AddMessage(f"Search term: '{search_term}'")
        arcpy.AddMessage(f"Similarity threshold: {cutoff*100:.0f}%")
        arcpy.AddMessage(f"Verbose mode: {'ON' if verbose else 'OFF'}")
        
        # Collect APRX files
        arcpy.AddMessage("=" * 80)
        aprx_files = collect_aprx_files(folder_path, verbose)
        
        if not aprx_files:
            arcpy.AddWarning("No APRX files found in folder")
        
        # Search all APRX files
        arcpy.AddMessage("=" * 80)
        arcpy.AddMessage("SCANNING APRX FILES")
        arcpy.AddMessage("=" * 80)
        
        results = search_all_aprx_files(aprx_files, search_term, cutoff, verbose)
        
        # Report results
        report_results(results, search_term, cutoff)
        
        arcpy.AddMessage("\n✓ Geoprocessing complete!")
        
    except Exception as e:
        arcpy.AddError(f"Tool execution failed: {str(e)}")
        raise
