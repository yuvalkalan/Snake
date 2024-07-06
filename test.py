import os
from PIL import Image

def resize_images_in_directory(input_directory, output_directory, new_width, new_height):
    try:
        # Create the output directory if it doesn't exist
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # List all files in the input directory
        files = os.listdir(input_directory)

        for file_name in files:
            if file_name.lower().endswith((".jpg", ".jpeg", ".png")):
                input_path = os.path.join(input_directory, file_name)
                output_path = os.path.join(output_directory, file_name)

                # Open the input image
                img = Image.open(input_path)

                # Resize the image
                resized_img = img.resize((new_width, new_height), Image.ANTIALIAS)

                # Save the resized image
                resized_img.save(output_path)
                print(f"Resized and saved: {file_name}")

        print("All images resized and saved successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Specify the input and output directories, new width, and new height
input_directory = r"C:\Users\yuval's workshop\Desktop\first"  # Replace with your input directory path
output_directory = r"C:\Users\yuval's workshop\Desktop\second"  # Replace with your desired output directory path
new_width = 1080  # Replace with the desired new width in pixels
new_height = 1080  # Replace with the desired new height in pixels

# Resize images in the directory
resize_images_in_directory(input_directory, output_directory, new_width, new_height)
