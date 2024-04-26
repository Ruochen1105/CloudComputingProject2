# CloudComputingProject2

## Cloud-Based Active (IAN) Application

"This part of the project focuses on the design and implementation of a Cloud application framework that operate on a P2P/Decentralized network (e.g., Hybrid Web2/Web 3 App network). The project also includes the design and implementation of a Cloud semi-independent IAN application. Specific projects will be discussed in class.

## File Structure

```bash
.
├── README.md
├── .gitignore
└── code
    ├── IoT
    ├── scripts
    │   ├── local_config.py  # store credentials
    │   └── sampling.py      # sample images from datasets
    └── python-p2p           # p2p framework
```

## local_config.py

```python
from os import path

ROOT_PATH = path.join("path to root folder of datasets")
DESTINATION_PATH = path.join("root to destination of sampled images")
```

## Dataset

The images without accidents are from [Traffic Detection Project](https://www.kaggle.com/datasets/yusufberksardoan/traffic-detection-project/data).

The images with accidents are from [Vehicle Crash Dataset Computer Vision Project](https://universe.roboflow.com/object-detection-3iugc/vehicle-crash-dataset).

These two datasets are sharing the following YOLOv8 file structure, except that "Vehicle Crash Dataset Computer Vision Project" does not have "valid" and "test":
```bash
.                    # root
├── ...              # meta info
├── test
│   ├── labels       # not used
│   └── images
│       ├── ...
│       └── {image_name}.jpg
├── trian
│   └── ...
└── valid
    └── ...
```

The dataset used in this project is randomly sampled from all images of the two public datasets. The script used is `./code/scripts/sampling.py`.

## References

### P2P Framework

[python-p2p](https://github.com/GianisTsol/python-p2p)

### gitignore

[A collection of .gitignore templates](https://github.com/github/gitignore)
