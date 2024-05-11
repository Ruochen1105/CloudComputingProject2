# CloudComputingProject2

## Cloud-Based Active (IAN) Application

"This part of the project focuses on the design and implementation of a Cloud application framework that operate on a P2P/Decentralized network (e.g., Hybrid Web2/Web 3 App network). The project also includes the design and implementation of a Cloud semi-independent IAN application. Specific projects will be discussed in class.

## File Structure

```

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
```
.
├── README.md
├── assets
├── code
│   ├── IoT
│   │   ├── IoT.py
│   │   ├── __init__.py
│   │   ├── cloudcomputing-415100-a9f3f6179657.json
│   │   ├── local_config.py
│   │   └── reader.py
│   ├── access_server.py
│   ├── node.py
│   ├── p2pnetwork
│   │   ├── __init__.py
│   │   ├── node.py
│   │   ├── nodeconnection.py
│   │   └── tests
│   │       ├── __init__.py
│   │       ├── test_node.py
│   │       ├── test_node_compression.py
│   │       └── test_nodeconnection.py
│   └── scripts
│       ├── local_config.py
│       └── sampling.py
└── requirements.txt
```

The dataset used in this project is randomly sampled from all images of the two public datasets. The script used is `./code/scripts/sampling.py`.

## References

### P2P Framework

[python-p2p-network](https://github.com/macsnoeren/python-p2p-network)

### gitignore

[A collection of .gitignore templates](https://github.com/github/gitignore)
