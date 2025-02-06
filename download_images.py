import os
import requests
from urllib.parse import urlparse

def download_image(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {filename}")
    else:
        print(f"Failed to download {filename}")

# Create images directory if it doesn't exist
images_dir = "images"
if not os.path.exists(images_dir):
    os.makedirs(images_dir)

# Dictionary of image URLs from Unsplash
images = {
    "hero-path.jpg": "https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=1600&q=80",  # Laboratory interior
    "blood-test.jpg": "https://images.unsplash.com/photo-1615461066841-6116e61058f4?w=800&q=80",  # Blood test
    "histopathology.jpg": "https://images.unsplash.com/photo-1579154204601-01588f351e67?w=800&q=80",  # Microscope
    "microbiology.jpg": "https://images.unsplash.com/photo-1576086213369-97a306d36557?w=800&q=80",  # Petri dish
    "automated-analyzer.jpg": "https://images.unsplash.com/photo-1582560474992-385ebb8d81ce?w=800&q=80",  # Lab equipment
    "collection-center.jpg": "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=800&q=80",  # Medical center
    "lab-facility.jpg": "https://images.unsplash.com/photo-1581093588401-fbb62a02f120?w=800&q=80",  # Modern lab
    "blood-analysis.jpg": "https://images.unsplash.com/photo-1579154204914-29e5b71b0891?w=800&q=80",  # Blood analysis
    "pathology.jpg": "https://images.unsplash.com/photo-1576671081837-49000212a370?w=800&q=80",  # Pathology lab
    "microscopy.jpg": "https://images.unsplash.com/photo-1516549655169-df83a0774514?w=800&q=80",  # Microscope close-up
    "report-analysis.jpg": "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=800&q=80",  # Medical report
    "pathologist1.jpg": "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=800&q=80",  # Female doctor
    "pathologist2.jpg": "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=800&q=80",  # Male doctor
    "technologist.jpg": "https://images.unsplash.com/photo-1581056771107-24ca5f033842?w=800&q=80",  # Lab technician
}

# Download each image
for filename, url in images.items():
    filepath = os.path.join(images_dir, filename)
    download_image(url, filepath)
