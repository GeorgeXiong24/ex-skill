#!/usr/bin/env python3
"""
Save relationship analysis profile to JSON file.
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path

def save_profile(analysis_data, profile_name="Anonymous"):
    """Save analysis data to JSON file.

    Args:
        analysis_data: Dictionary containing analysis results
        profile_name: Name or identifier for the ex-partner

    Returns:
        Path to saved JSON file
    """
    # Create storage directory
    home = Path.home()
    storage_dir = home / ".claude" / "relationship_analysis" / "profiles"
    storage_dir.mkdir(parents=True, exist_ok=True)

    # Generate profile ID
    profile_id = str(uuid.uuid4())[:8]

    # Prepare full data structure
    profile = {
        "profile_id": profile_id,
        "ex_partner_name": profile_name,
        "analysis_date": datetime.now().isoformat(),
        "linguistic_style": analysis_data.get("linguistic_style", {}),
        "behavioral_patterns": analysis_data.get("behavioral_patterns", {}),
        "core_traits": analysis_data.get("core_traits", {}),
        "relationship_dynamics": analysis_data.get("relationship_dynamics", {}),
        "quantitative_metrics": analysis_data.get("quantitative_metrics", {}),
        "source_files": analysis_data.get("source_files", []),
        "extracted_text_preview": analysis_data.get("extracted_text_preview", "")[:1000],
        "full_report": analysis_data.get("full_report", "")
    }

    # Save to file
    filename = f"{profile_id}_{profile_name.replace(' ', '_')}.json"
    filepath = storage_dir / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)

    return str(filepath)

if __name__ == "__main__":
    # Example usage
    sample_data = {
        "linguistic_style": {"tone": "casual", "emoji_usage": "frequent"},
        "behavioral_patterns": {"conflict_resolution": "avoidant"},
        "source_files": ["conversation.txt"],
        "extracted_text_preview": "Sample conversation text...",
        "full_report": "# Behavioral Analysis Report..."
    }

    saved_path = save_profile(sample_data, "TestProfile")
    print(f"Profile saved to: {saved_path}")