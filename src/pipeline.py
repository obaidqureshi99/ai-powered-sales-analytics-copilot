import pandas as pd
from pathlib import Path

from src.cleaning import clean_sales_data
from src.validation import validate_sales_data
from src.logger import get_logger


PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_PATH = PROJECT_ROOT / "data" / "raw" / "Superstore.csv"

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_PATH = PROCESSED_DIR / "superstore_cleaned.csv"

logger = get_logger()


def run_pipeline():

    try:
        logger.info("Sales pipeline started.")

        # Load raw data
        df = pd.read_csv(RAW_PATH, encoding="latin1")
        logger.info(f"Raw dataset loaded: {df.shape}")

        # Clean data
        cleaned_df = clean_sales_data(df)
        logger.info(f"Cleaning completed: {cleaned_df.shape}")

        # Validate data
        errors = validate_sales_data(cleaned_df)

        if errors:
            for error in errors:
                logger.error(error)

            raise ValueError("Data validation failed.")

        # Save processed data
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

        cleaned_df.to_csv(PROCESSED_PATH, index=False)

        logger.info("Processed dataset saved successfully.")
        logger.info("Sales pipeline completed.")

        print("Pipeline completed successfully!")
        print(f"Original rows: {len(df)}")
        print(f"Cleaned rows: {len(cleaned_df)}")
        print(f"Saved file: {PROCESSED_PATH}")

    except Exception:
        logger.exception("Pipeline failed.")
        raise


if __name__ == "__main__":
    run_pipeline()