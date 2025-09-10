import json
import os
from config import LAST_UPDATED, VERSION, DATA_SOURCES
from score_data import score_all

def build_all():
    print("Building the final civi.json database...")
    # This would take the final scores and build the json file.
    final_data = {
        "metadata": {
            "last_updated": LAST_UPDATED,
            "source_version": VERSION,
            "sources": list(DATA_SOURCES.keys())
        },
        "countries": score_all()
    }

    data_dir = "../data"
    os.makedirs(data_dir, exist_ok=True)
    with open(os.path.join(data_dir, "civi.json"), "w") as f:
        json.dump(final_data, f, indent=2)

    print("civi.json built successfully.")

if __name__ == "__main__":
    build_all()
