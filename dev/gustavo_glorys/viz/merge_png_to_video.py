import cv2
import os
from pathlib import Path

for output_var in ["mlotst","ssh"]:
    # Set input and output paths
    image_folder = f"/glade/u/home/manishrv/documents/croc/dev/gustavo_glorys/plots/glorys_vs_cesm/{output_var}/monthly_plots"   # Folder containing PNGs
         # Output video filename
    
    for fps,label in [(1,"slow"),(30,"fast")]:
        output_video = f"/glade/u/home/manishrv/documents/croc/dev/gustavo_glorys/plots/glorys_vs_cesm/{output_var}/monthly_cesm_glorys_{label}.mp4"
        # Get all PNG files and sort them by filename
        images = sorted(Path(image_folder).glob("*.png"))
        
        # Check if there are images
        if not images:
            print(image_folder)
            print("No PNG images found in the folder.")
            exit()
        
        # Get image dimensions
        frame = cv2.imread(str(images[0]))
        height, width, layers = frame.shape
        
        # Define the codec and create the VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use 'XVID' for .avi output
        video = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
        
        # Add images to the video
        for img_path in images:
            img = cv2.imread(str(img_path))
            video.write(img)
        
        # Release resources
        video.release()
        print(f"Video saved as {output_video}")
