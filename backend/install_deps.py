"""Helper script to install dependencies, handling rasterio separately."""
import subprocess
import sys


def install_requirements():
    """Install requirements, handling rasterio separately if needed."""
    print("Installing base requirements...")
    
    # Install everything except rasterio first
    base_packages = [
        "fastapi==0.115.0",
        "uvicorn[standard]==0.32.0",
        "python-multipart==0.0.12",
        "boto3==1.40.66",
        "langchain-openai==0.3.35",
        "langchain-community==0.3.31",
        "langchain==0.3.27",
        "openai==2.3.0",
        "faiss-cpu==1.12.0",
        "pillow==11.1.0",
        "numpy>=1.26.4,<3.0.0",
        "pydantic==2.11.7",
        "pydantic-settings==2.11.0",
        "python-dotenv==1.0.1",
        "geopy==2.4.1",
    ]
    
    for package in base_packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to install {package}: {e}")
    
    # Try to install rasterio separately
    print("\nAttempting to install rasterio...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "rasterio>=1.3.9,<2.0.0"])
        print("✓ rasterio installed successfully")
    except subprocess.CalledProcessError:
        print("⚠ rasterio installation failed. The app will still work but GeoTIFF centroid extraction will be disabled.")
        print("To install rasterio later, try:")
        print("  pip install rasterio")
        print("  or")
        print("  conda install -c conda-forge rasterio")
    
    print("\n✓ Installation complete!")


if __name__ == "__main__":
    install_requirements()

