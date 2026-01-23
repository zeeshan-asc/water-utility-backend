"""
Training Data Manager for Vanna AI

This utility helps manage training data in your Vanna model:
- View existing training data
- Remove specific training data
- Clear all training data for fresh start
- Smart updates (remove old, add new)

Usage:
    python training_data_manager.py
"""

import os
import sys
import logging
from typing import Optional
from dotenv import load_dotenv
from core.custom_vanna import MyVanna


def setup_logging() -> None:
    """Configure logging for the manager."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def initialize_vanna():
    """Initialize Vanna instance with same config as training script."""
    load_dotenv()
    
    logger = logging.getLogger(__name__)
    logger.info("Initializing Vanna AI instance...")
    
    # Initialize custom Vanna instance
    vn = MyVanna(config={
        'model': 'gpt-4o-mini',
        'temperature': 0.7,
    })
    
    logger.info("Vanna AI instance initialized successfully")
    return vn


def view_training_data(vn) -> None:
    """Display all current training data."""
    try:
        print("\n" + "="*60)
        print("CURRENT TRAINING DATA")
        print("="*60)
        
        training_data = vn.get_training_data()
        
        if training_data is None or len(training_data) == 0:
            print("No training data found in the model.")
            return
        
        print(f"Total training records: {len(training_data)}")
        
        # Group by training data type
        if 'training_data_type' in training_data.columns:
            type_counts = training_data['training_data_type'].value_counts()
            print("\nTraining data by type:")
            for data_type, count in type_counts.items():
                print(f"  {data_type}: {count} records")
        
        # Show detailed records
        print("\nDetailed records:")
        for index, row in training_data.iterrows():
            print(f"\nID: {row['id']}")
            print(f"Type: {row['training_data_type']}")
            if 'question' in row and row['question']:
                print(f"Question: {row['question'][:100]}...")
            if 'content' in row and row['content']:
                content_preview = str(row['content'])[:200].replace('\n', ' ')
                print(f"Content: {content_preview}...")
        
        print("="*60)
        
    except Exception as e:
        print(f"Error viewing training data: {e}")
        import traceback
        traceback.print_exc()


def remove_training_data_by_type(vn, data_type: str) -> bool:
    """Remove all training data of a specific type."""
    try:
        training_data = vn.get_training_data()
        
        if training_data is None or len(training_data) == 0:
            print("No training data found to remove.")
            return True
        
        # Filter by type
        records_to_remove = training_data[training_data['training_data_type'] == data_type]
        
        if len(records_to_remove) == 0:
            print(f"No training data of type '{data_type}' found.")
            return True
        
        print(f"Found {len(records_to_remove)} records of type '{data_type}' to remove...")
        
        removed_count = 0
        for index, row in records_to_remove.iterrows():
            try:
                vn.remove_training_data(id=row['id'])
                removed_count += 1
                if removed_count % 10 == 0:
                    print(f"  Removed {removed_count}/{len(records_to_remove)}...")
            except Exception as e:
                print(f"Failed to remove {row['id']}: {e}")
        
        print(f"Successfully removed {removed_count}/{len(records_to_remove)} records")
        return removed_count == len(records_to_remove)
        
    except Exception as e:
        print(f"Error removing training data: {e}")
        import traceback
        traceback.print_exc()
        return False


def clear_all_training_data(vn) -> bool:
    """Remove ALL training data from the model."""
    try:
        training_data = vn.get_training_data()
        
        if training_data is None or len(training_data) == 0:
            print("No training data found to clear.")
            return True
        
        print(f"Found {len(training_data)} total records to remove...")
        
        # Confirm with user
        confirm = input(f"Are you sure you want to remove ALL {len(training_data)} training records? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Operation cancelled.")
            return False
        
        removed_count = 0
        total = len(training_data)
        for index, row in training_data.iterrows():
            try:
                vn.remove_training_data(id=row['id'])
                removed_count += 1
                if removed_count % 10 == 0:
                    print(f"  Removed {removed_count}/{total}...")
            except Exception as e:
                print(f"Failed to remove {row['id']}: {e}")
        
        print(f"Successfully removed {removed_count}/{total} records")
        return removed_count == total
        
    except Exception as e:
        print(f"Error clearing training data: {e}")
        import traceback
        traceback.print_exc()
        return False


def remove_by_id(vn, record_id: str) -> bool:
    """Remove a specific training data record by ID."""
    try:
        vn.remove_training_data(id=record_id)
        print(f"Successfully removed record: {record_id}")
        return True
    except Exception as e:
        print(f"Error removing record {record_id}: {e}")
        return False


def main():
    """Main menu for training data management."""
    setup_logging()
    
    print("="*60)
    print("Vanna AI Training Data Manager")
    print("="*60)
    
    try:
        vn = initialize_vanna()
        print("Successfully connected to Vanna AI model")
        
        while True:
            print("\nOptions:")
            print("1. View all training data")
            print("2. Remove DDL training data")
            print("3. Remove documentation training data") 
            print("4. Remove SQL training data")
            print("5. Clear ALL training data (fresh start)")
            print("6. Remove specific record by ID")
            print("7. Exit")
            
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == '1':
                view_training_data(vn)
            
            elif choice == '2':
                print("\nRemoving DDL training data...")
                remove_training_data_by_type(vn, 'ddl')
            
            elif choice == '3':
                print("\nRemoving documentation training data...")
                remove_training_data_by_type(vn, 'documentation')
            
            elif choice == '4':
                print("\nRemoving SQL training data...")
                remove_training_data_by_type(vn, 'sql')
            
            elif choice == '5':
                print("\nClearing ALL training data...")
                clear_all_training_data(vn)
            
            elif choice == '6':
                record_id = input("\nEnter record ID to remove: ").strip()
                if record_id:
                    remove_by_id(vn, record_id)
                else:
                    print("Invalid record ID")
            
            elif choice == '7':
                print("Goodbye!")
                break
            
            else:
                print("Invalid choice. Please enter 1-7.")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)




