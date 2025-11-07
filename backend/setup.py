"""Setup script to create necessary directories and check configuration."""
import os
from pathlib import Path


def create_directories():
    """Create necessary directories for the application."""
    dirs = [
        "uploads",
        "images_jpeg",
        "vectorstore"
    ]
    
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✓ Created directory: {dir_name}")


def check_env_file():
    """Check if .env file exists and has required variables."""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("⚠ .env file not found!")
        print("Please create a .env file with the following variables:")
        print("\nRequired:")
        print("  OPENAI_API_KEY=your_openai_api_key")
        print("  AWS_ACCESS_KEY_ID=your_aws_access_key")
        print("  AWS_SECRET_ACCESS_KEY=your_aws_secret_key")
        print("  AWS_S3_BUCKET=your_s3_bucket_name")
        print("\nOptional:")
        print("  AWS_DEFAULT_REGION=us-west-1")
        print("  LANGCHAIN_API_KEY=your_langchain_api_key")
        print("\nYou can copy .env.example to .env and fill in the values.")
        return False
    else:
        print("✓ .env file found")
        return True


def check_required_packages():
    """Check if required packages are installed."""
    required = [
        "fastapi",
        "uvicorn",
        "langchain_openai",
        "openai",
        "boto3",
        "faiss"
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package} installed")
        except ImportError:
            print(f"✗ {package} NOT installed")
            missing.append(package)
    
    # Check rasterio separately (optional)
    try:
        import rasterio
        print("✓ rasterio installed (GeoTIFF support enabled)")
    except ImportError:
        print("⚠ rasterio not installed (GeoTIFF centroid extraction disabled)")
    
    if missing:
        print(f"\n⚠ Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True


def main():
    """Run setup checks."""
    print("=" * 50)
    print("ImageRAG Backend Setup")
    print("=" * 50)
    print()
    
    print("1. Creating directories...")
    create_directories()
    print()
    
    print("2. Checking .env file...")
    env_ok = check_env_file()
    print()
    
    print("3. Checking required packages...")
    packages_ok = check_required_packages()
    print()
    
    print("=" * 50)
    if env_ok and packages_ok:
        print("✓ Setup complete! You can now run the server:")
        print("  uvicorn app.main:app --reload")
    else:
        print("⚠ Setup incomplete. Please fix the issues above.")
    print("=" * 50)


if __name__ == "__main__":
    main()

