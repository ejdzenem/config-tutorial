import logging
import os

from src.settings import load_settings, Settings

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting the application...")

    # Load settings (default config)
    os.environ["OUTPUT_BUCKET"] = "my_bucket"  # needed for the placeholder in config
    settings: Settings = load_settings()

    print(f"Input table name: {settings.table_names.input_table}")
    print(f"Input data path: {settings.data_paths.input_path}")

    # Override settings with ENV vars
    os.environ["TABLE_NAMES__INPUT_TABLE"] = "some_new_input_table"
    os.environ["DATA_PATHS__INPUT_PATH"] = "s3://my_new_bucket/new_path/to/input/data"
    # And load settings (default config)
    settingsEnv: Settings = load_settings()

    print(f"New input table name: {settingsEnv.table_names.input_table}")
    print(f"New OUTPUT table name: {settingsEnv.table_names.output_table}")
    print(f"Unchanged input data path: {settingsEnv.data_paths.input_path}")
