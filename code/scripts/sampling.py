import os
import random
import shutil

from ..local_config import ROOT_PATH, DESTINATION_PATH
NUMBER_OF_PHOTOS = 10
SEED = "CloudComputing2024Spring"

if __name__ == "__main__":
    random.seed(SEED)
    image_folder_paths = []
    for split in ["train", "valid", "test"]:
        image_folder_paths.append(os.path.join(ROOT_PATH, split, "images"))
    image_paths = []
    for image_folder_path in image_folder_paths:
        for _, _, images in os.walk(image_folder_path):
            for image in images:
                image_paths.append(os.path.join(image_folder_path, image))
    sampled = random.sample(image_paths, k=NUMBER_OF_PHOTOS)
    print(sampled)
    for id, sample in enumerate(sampled):
        shutil.copyfile(src=sample, dst=os.path.join(DESTINATION_PATH, str(id) + ".png"))
