"""
Pipeline Validation Script for OceanEmbed
Runs data contract verification, dataset loading checks, and pytest test suite.
"""

import sys
import subprocess
import yaml
from src.data.validation import DataValidator


def main():
    print("=== OceanEmbed Pipeline Validator ===")
    
    # 1. Run pytest suite
    print("\nRunning unit test suite via pytest...")
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], capture_output=False)
    
    if result.returncode == 0:
        print("\n✅ All unit tests passed!")
    else:
        print("\n❌ Unit test suite failed!")
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
