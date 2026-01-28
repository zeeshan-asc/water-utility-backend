"""
Quick script to clear all training data from Vanna AI.

Usage:
    python clear_training_data.py
"""

import os
import sys
import logging
from dotenv import load_dotenv
from core.custom_vanna import MyVanna

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()


def clear_all_training_data():
    """Clear all training data from Vanna."""
    try:
        logger.info("Initializing Vanna AI instance...")
        vn = MyVanna(config={
            'model': 'gpt-4o-mini',
            'temperature': 0.7,
        })
        logger.info("Vanna AI instance initialized successfully")
        
        logger.info("Retrieving existing training data...")
        training_data = vn.get_training_data()
        
        if training_data is None or len(training_data) == 0:
            logger.info("No training data found. Nothing to clear.")
            return True
        
        total_records = len(training_data)
        logger.info(f"Found {total_records} training records to remove")
        
        # Group by type for summary
        if 'training_data_type' in training_data.columns:
            type_counts = training_data['training_data_type'].value_counts()
            logger.info("Training data by type:")
            for data_type, count in type_counts.items():
                logger.info(f"  {data_type}: {count} records")
        
        logger.info("Removing all training data...")
        removed_count = 0
        
        for index, row in training_data.iterrows():
            try:
                vn.remove_training_data(id=row['id'])
                removed_count += 1
                if removed_count % 10 == 0:
                    logger.info(f"  Removed {removed_count}/{total_records}...")
            except Exception as e:
                logger.error(f"Failed to remove {row['id']}: {e}")
        
        logger.info(f"Successfully removed {removed_count}/{total_records} records")
        
        # Verify deletion
        remaining_data = vn.get_training_data()
        if remaining_data is None or len(remaining_data) == 0:
            logger.info("✓ All training data cleared successfully!")
            return True
        else:
            logger.warning(f"Warning: {len(remaining_data)} records still remain")
            return False
            
    except Exception as e:
        logger.error(f"Error clearing training data: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    print("="*60)
    print("Clearing All Vanna AI Training Data")
    print("="*60)
    print()
    
    success = clear_all_training_data()
    
    if success:
        print("\n" + "="*60)
        print("SUCCESS: All training data has been cleared!")
        print("="*60)
        print("\nYou can now retrain with new data using:")
        print("  python train_vanna.py")
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("ERROR: Failed to clear all training data")
        print("="*60)
        sys.exit(1)









