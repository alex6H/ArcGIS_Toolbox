#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This ArcGIS Pro tool checks group membership for specified portal items and manages user access.

Core functionality:
- Connects to active ArcGIS Portal using "pro" authentication
- Finds target user by email address
- Retrieves items by ID and identifies associated groups
- Checks if target user is member/owner of each group
- Optionally adds user to groups they're not in
- Optionally transfers item ownership to target user

Key features:
- Handles multiple item IDs (semicolon-separated)
- Skips Favorites groups (system groups)
- Prevents duplicate group processing
- Comprehensive error handling with arcpy messaging
- Returns detailed summary statistics

File : item_group_membership_checker.py
Author: github.com/alex6H
"""

import arcpy
from typing import List, Dict, Any, Optional, Tuple, Set
from arcgis.gis import GIS


def get_portal_connection(verbose: bool) -> Optional[GIS]:
    """
    Establish a connection to the active ArcGIS Portal.

    Args:
        verbose: Print debug messages.

    Returns:
        Authenticated GIS object or None if connection fails.
    """
    try:
        # Attempt to connect to the ArcGIS Portal
        gis = GIS("pro")
        if verbose:
            arcpy.AddMessage(f"✅ Connected to {gis.properties.portalName} as {gis.users.me.username}")
        return gis
    except Exception as e:
        arcpy.AddError(f"❌ Failed to connect to portal: {str(e)}")
        return None

def get_user_by_email(gis: GIS, email: str, verbose: bool) -> Optional[Any]:
    """
    Find a portal user by their email address.

    Args:
        gis: Authenticated GIS object.
        email: Email address of the target user.
        verbose: Print debug messages.

    Returns:
        User object or None if not found.
    """
    try:
        # Search for the user by email
        results = gis.users.search(query=email, max_users=1)
        if not results:
            arcpy.AddWarning(f"❌ No user found with email: {email}")
            return None
        user = results[0]
        if verbose:
            arcpy.AddMessage(f"✅ Found target user: {user.username} ({user.fullName})")
        return user
    except Exception as e:
        arcpy.AddError(f"❌ Error searching for user '{email}': {str(e)}")
        return None

def get_item_details(gis: GIS, item_id: str, verbose: bool) -> Optional[Any]:
    """Retrieve item by ID."""
    try:
        # Attempt to retrieve the item details
        item = gis.content.get(item_id)
        if item:
            if verbose:
                arcpy.AddMessage(f"Found item: {item.title} (Type: {item.type})")
            return item
        else:
            arcpy.AddWarning(f"Item with ID '{item_id}' not found")
            return None
    except Exception as e:
        arcpy.AddError(f"Error retrieving item {item_id}: {str(e)}")
        return None

def get_groups_for_item(gis: GIS, item: Any, verbose: bool) -> List[Any]:
    """Get groups an item is shared with."""
    try:
        # Retrieve groups the item is shared with
        sharing_details = item.shared_with
        group_ids = sharing_details.get('groups', [])
        groups = []
        if verbose:
            arcpy.AddMessage(f"\n=== Checking related groups ===")

        for group_item in group_ids:
            try:
                # Attempt to retrieve each group by ID
                group = gis.groups.get(group_item.id)
                if group:
                    groups.append(group)
                    if verbose:
                        arcpy.AddMessage(f"Group: {group.title} (ID: {group.id})")
            except Exception as e:
                arcpy.AddWarning(f"Error retrieving group with ID '{group_item.id}': {str(e)}")
        return groups
    except Exception as e:
        arcpy.AddError(f"Error getting groups for item {item.id}: {str(e)}")
        return []


def is_favorites_group(group: Any) -> bool:
    """Check if group is a Favorites group."""
    return "Favorites" in group.title


def check_user_in_group(group: Any, target_user: Any, verbose: bool) -> bool:
    """
    Check if the target user is in the group or is the owner.
    """
    try:
        # Determine if the target user is the owner of the group
        is_owner = group.owner == target_user.username
        
        # Retrieve group members and check if the target user is a member
        members = group.get_members()
        is_member = (
            target_user.username in members.get('users', []) or
            target_user.username in members.get('admins', [])
        )

        # Log the membership status
        if is_owner:
            arcpy.AddMessage(f"✅ User '{target_user.username}' is the owner of group '{group.title}'.")
        elif is_member:
            arcpy.AddMessage(f"✅ User '{target_user.username}' is a member of group '{group.title}'.")
        else:
            arcpy.AddMessage(f"❌ User '{target_user.username}' is not a member of group '{group.title}'.")
        
        # Return membership status
        return is_owner or is_member
    except Exception as e:
        arcpy.AddError(f"Error checking membership for group '{group.title}': {str(e)}")
        return False


def add_user_to_group(group: Any, target_user: Any, verbose: bool) -> bool:
    """
    Add target user as a member to a group.
    """
    try:
        # Check if the user is already the owner of the group
        if group.owner == target_user.username:
            arcpy.AddWarning(f"User '{target_user.username}' is already the owner of '{group.title}'.")
            return True
        
        # Skip adding to Favorites group
        if is_favorites_group(group):
            arcpy.AddWarning(f"Skipping Favorites group: '{group.title}'.")
            return False
        
        # Check if the user is already a member
        members = group.get_members()
        if target_user.username in members.get('users', []) or target_user.username in members.get('admins', []):
            arcpy.AddWarning(f"User '{target_user.username}' already a member of '{group.title}'.")
            return True
        
        # Attempt to add the user to the group
        result = group.add_users([target_user.username])
        if result.get('notAdded'):
            arcpy.AddWarning(f"❌ Could not add '{target_user.username}' to '{group.title}': {result.get('notAdded')}")
            return False
        
        # Log successful addition
        arcpy.AddMessage(f"✅ Added '{target_user.username}' to group '{group.title}'.")
        return True
    except Exception as e:
        arcpy.AddWarning(f"Error adding user to group '{group.title}': {str(e)}")
        return False


def take_item_ownership(item: Any, target_user: Any, verbose: bool) -> bool:
    """
    Transfer ownership of the item to the target user.
    """
    try:
        # Check if the target user already owns the item
        if item.owner == target_user.username:
            arcpy.AddMessage(f"✅ '{target_user.username}' already owns '{item.title}'.")
            return True
        
        # Attempt to transfer ownership
        result = item.reassign_to(target_user.username)
        if result:
            arcpy.AddMessage(f"✅ Ownership of '{item.title}' transferred to '{target_user.username}'.")
            return True
        else:
            arcpy.AddWarning(f"❌ Failed to transfer ownership of '{item.title}'.")
            return False
    except Exception as e:
        arcpy.AddWarning(f"Error taking ownership of '{item.title}': {str(e)}")
        return False


def process_items(
    gis: GIS,
    target_user: Any,
    item_ids: List[str],
    add_to_groups: bool,
    take_ownership_flag: bool,
    verbose: bool
) -> Tuple[int, int, int, int, int]:
    """
    Process each item for the target user.
    """
    items_processed = 0
    total_groups = 0
    groups_user_is_in = 0
    groups_user_added_to = 0
    items_ownership_taken = 0
    processed_group_ids: Set[str] = set()

    for item_id in item_ids:
        # Process each item ID
        if verbose:
            arcpy.AddMessage(f"\n--- Processing Item ID: {item_id} ---")
        item = get_item_details(gis, item_id, verbose)
        if not item:
            continue
        items_processed += 1
        groups = get_groups_for_item(gis, item, verbose)
        
        # Check membership for each group associated with the item
        if verbose:
            arcpy.AddMessage(f"\n=== Checking membership for groups ===")
        for group in groups:
            if group.id in processed_group_ids:
                if verbose:
                    arcpy.AddMessage(f"Skipping already processed group: {group.title} (ID: {group.id})")
                continue
            processed_group_ids.add(group.id)
            total_groups += 1
            if verbose:
                arcpy.AddMessage(f"Checking membership for group: {group.title} (ID: {group.id})")
            is_member = check_user_in_group(group, target_user, verbose)
            if is_member:
                groups_user_is_in += 1
            elif add_to_groups:
                # Add user to group if not already a member
                if verbose:
                    arcpy.AddMessage(f"Attempting to add user to group: {group.title} (ID: {group.id})")
                if add_user_to_group(group, target_user, verbose):
                    groups_user_added_to += 1
                    groups_user_is_in += 1

        # Take ownership of the item if the flag is set and user is in groups
        if take_ownership_flag and groups_user_is_in > 0:
            if verbose:
                arcpy.AddMessage(f"\n=== Take Item Ownership ===")
                arcpy.AddMessage(f"Attempting to take ownership of item: {item.title} (ID: {item.id})")
            if take_item_ownership(item, target_user, verbose):
                items_ownership_taken += 1

    return items_processed, total_groups, groups_user_is_in, groups_user_added_to, items_ownership_taken


if __name__ == "__main__":
    try:
        # Parameters
        item_ids_string = arcpy.GetParameterAsText(0)
        add_to_groups = arcpy.GetParameter(1)
        take_ownership_flag = arcpy.GetParameter(2)
        target_email = arcpy.GetParameterAsText(3)
        verbose = arcpy.GetParameter(4)

        if not target_email:
            arcpy.AddError("❌ Target email is required.")
            raise SystemExit

        gis = get_portal_connection(verbose)
        if not gis:
            raise SystemExit

        target_user = get_user_by_email(gis, target_email, verbose)
        if not target_user:
            raise SystemExit

        item_ids = [iid.strip() for iid in item_ids_string.split(";") if iid.strip()]
        if not item_ids:
            arcpy.AddError("❌ No valid item IDs provided.")
            raise SystemExit

        results = process_items(gis, target_user, item_ids, add_to_groups, take_ownership_flag, verbose)

        arcpy.AddMessage("\n--- SUMMARY ---")
        arcpy.AddMessage(f"Items processed: {results[0]}")
        arcpy.AddMessage(f"Groups found: {results[1]}")
        arcpy.AddMessage(f"Groups target user is in: {results[2]}")
        arcpy.AddMessage(f"Groups target user added to: {results[3]}")
        arcpy.AddMessage(f"Items ownership taken: {results[4]}")

    except Exception as e:
        arcpy.AddError(f"Unexpected error: {str(e)}")
