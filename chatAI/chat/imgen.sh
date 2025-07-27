#! /bin/bash
# This script is used to run the image generation script with the correct environment variables.

source /mnt/AI/AI/imageAI/comfy-env/bin/activate
python3 /mnt/AI/AI/imageAI/AI-Image-Generator/chatAI-ImgGen.py \
  --prompt "$1"

if [ $? -eq 0 ]; then
    echo "Image generation completed successfully."
else
    echo "Image generation failed."
fi  

deactivate
echo "Environment deactivated."
