#!/usr/bin/env python3
import json
import sys
import os
from datetime import datetime

def main():
    if len(sys.argv) < 3:
        print("Usage: python info.py d=<draw_number> c=<combination>")
        print("Example: python info.py d=308900 c=13 3 21 15")
        sys.exit(1)
    
    # Parse arguments
    draw = None
    combination = None
    
    for arg in sys.argv[1:]:
        if arg.startswith('d='):
            draw = arg[2:]
        elif arg.startswith('c='):
            combination = ' '.join(arg[2:].split())
    
    # Handle case where combination is split across multiple arguments
    if not combination:
        combo_parts = []
        for arg in sys.argv[1:]:
            if not arg.startswith('d=') and not arg.startswith('c='):
                combo_parts.append(arg)
        if combo_parts:
            combination = ' '.join(combo_parts)
    
    if not draw or not combination:
        print("Error: Both draw number (d=) and combination (c=) are required")
        print("Usage: python info.py d=<draw_number> c=<combination>")
        sys.exit(1)
    
    file_path = "/opt/project/api_data/info.json"
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found")
        sys.exit(1)
    
    try:
        # Read current data
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Get the last entry from history to preserve its structure
        last_entry = None
        if data.get("history") and len(data["history"]) > 0:
            last_entry = data["history"][-1].copy()
        
        # Create new entry based on the last one or with default values
        if last_entry:
            new_entry = last_entry.copy()
            new_entry["draw"] = draw
            new_entry["combination"] = combination
            new_entry["processed"] = True
            # Keep original timestamp and processing_time if they exist
        else:
            # Create new entry if no history exists
            new_entry = {
                "draw": draw,
                "combination": combination,
                "timestamp": datetime.now().isoformat(),
                "processed": True,
                "service_type": "api_request"
            }
        
        # Update only specific fields in the main structure
        data["current_draw"] = draw
        # service_status remains unchanged
        data["history"] = [new_entry]
        
        # Write back to file
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Print the updated data structure for confirmation
        print(json.dumps(data, indent=2))
        
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
