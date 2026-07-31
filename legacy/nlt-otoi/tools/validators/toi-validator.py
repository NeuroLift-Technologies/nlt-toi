#!/usr/bin/env python3
"""
OTOI Personal TOI Validator

Validates Personal Terms of Interaction (TOI) files against the schema.
Supports neurodivergent users with clear error messages and helpful guidance.
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
import jsonschema
from jsonschema import Draft7Validator, ValidationError


class TOIValidator:
    """Validates Personal TOI files against the schema."""
    
    def __init__(self, schema_path: Optional[Path] = None):
        """Initialize the validator with the schema."""
        if schema_path is None:
            schema_path = Path(__file__).parent.parent / "schemas" / "v1.0" / "personal-toi-v1.json"
        
        self.schema_path = schema_path
        self.schema = self._load_schema()
        self.validator = Draft7Validator(self.schema)
    
    def _load_schema(self) -> Dict[str, Any]:
        """Load the JSON schema from file."""
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Error: Schema file not found at {self.schema_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON in schema file: {e}")
            sys.exit(1)
    
    def validate_file(self, toi_path: Path) -> bool:
        """
        Validate a TOI file against the schema.
        
        Args:
            toi_path: Path to the TOI file to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            with open(toi_path, 'r', encoding='utf-8') as f:
                toi_data = json.load(f)
        except FileNotFoundError:
            print(f"❌ Error: TOI file not found at {toi_path}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON in TOI file: {e}")
            return False
        
        return self.validate_data(toi_data, toi_path.name)
    
    def validate_data(self, toi_data: Dict[str, Any], filename: str = "TOI") -> bool:
        """
        Validate TOI data against the schema.
        
        Args:
            toi_data: The TOI data to validate
            filename: Name of the file for error reporting
            
        Returns:
            True if valid, False otherwise
        """
        try:
            self.validator.validate(toi_data)
            print(f"✅ {filename} is valid!")
            return True
        except ValidationError as e:
            self._print_validation_error(e, filename)
            return False
        except Exception as e:
            print(f"❌ Unexpected error validating {filename}: {e}")
            return False
    
    def _print_validation_error(self, error: ValidationError, filename: str):
        """Print a user-friendly validation error message."""
        print(f"❌ {filename} validation failed:")
        print()
        
        # Get the error path
        path = " -> ".join(str(p) for p in error.absolute_path) if error.absolute_path else "root"
        
        print(f"📍 Location: {path}")
        print(f"💬 Message: {error.message}")
        print()
        
        # Provide helpful guidance based on the error
        self._provide_guidance(error)
    
    def _provide_guidance(self, error: ValidationError):
        """Provide helpful guidance based on the validation error."""
        path = " -> ".join(str(p) for p in error.absolute_path) if error.absolute_path else "root"
        
        # Common error patterns and guidance
        if "required" in error.message.lower():
            print("💡 This field is required. Make sure to include it in your TOI.")
        elif "enum" in error.message.lower():
            print("💡 This field must be one of the allowed values. Check the schema for valid options.")
        elif "pattern" in error.message.lower():
            print("💡 This field doesn't match the required format. Check the schema for the correct pattern.")
        elif "type" in error.message.lower():
            print("💡 This field has the wrong data type. Check the schema for the expected type.")
        elif "additionalProperties" in error.message.lower():
            print("💡 This object contains properties that aren't allowed. Remove any extra properties.")
        
        # Specific guidance for common fields
        if "metadata" in path:
            print("📋 Make sure your metadata includes version, created_date, and last_updated.")
        elif "user_profile" in path:
            print("👤 Check that your user profile includes cognitive_patterns and communication_style.")
        elif "interaction_preferences" in path:
            print("🤝 Ensure your interaction preferences include response_style and task_management.")
        elif "data_governance" in path:
            print("🔒 Verify your data governance settings include data_retention and data_usage.")
        elif "accessibility_needs" in path:
            print("♿ Check that your accessibility needs are properly configured.")
        
        print()
        print("🔍 For more help, check the schema documentation or examples in the templates/ directory.")
    
    def validate_batch(self, toi_files: List[Path]) -> Dict[str, bool]:
        """
        Validate multiple TOI files.
        
        Args:
            toi_files: List of TOI file paths to validate
            
        Returns:
            Dictionary mapping file paths to validation results
        """
        results = {}
        
        print(f"🔍 Validating {len(toi_files)} TOI files...")
        print()
        
        for toi_file in toi_files:
            print(f"Validating {toi_file.name}...")
            results[str(toi_file)] = self.validate_file(toi_file)
            print()
        
        # Summary
        valid_count = sum(results.values())
        total_count = len(results)
        
        print(f"📊 Validation Summary:")
        print(f"   ✅ Valid: {valid_count}/{total_count}")
        print(f"   ❌ Invalid: {total_count - valid_count}/{total_count}")
        
        return results


def main():
    """Main entry point for the TOI validator."""
    parser = argparse.ArgumentParser(
        description="Validate Personal TOI files against the schema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python toi-validator.py my-toi.json
  python toi-validator.py *.json
  python toi-validator.py --schema custom-schema.json my-toi.json
        """
    )
    
    parser.add_argument(
        "toi_files",
        nargs="+",
        type=Path,
        help="TOI files to validate"
    )
    
    parser.add_argument(
        "--schema",
        type=Path,
        help="Path to custom schema file (default: schemas/v1.0/personal-toi-v1.json)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = TOIValidator(args.schema)
    
    # Validate files
    if len(args.toi_files) == 1:
        # Single file validation
        success = validator.validate_file(args.toi_files[0])
        sys.exit(0 if success else 1)
    else:
        # Batch validation
        results = validator.validate_batch(args.toi_files)
        all_valid = all(results.values())
        sys.exit(0 if all_valid else 1)


if __name__ == "__main__":
    main()