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
│   ├── accidents
│   │   ├── 0.png
│   │   ├── 1.png
│   │   ├── 2.png
│   │   ├── 3.png
│   │   ├── 4.png
│   │   ├── 5.png
│   │   ├── 6.png
│   │   ├── 7.png
│   │   ├── 8.png
│   │   └── 9.png
│   └── no_accidents
│       ├── 0.png
│       ├── 1.png
│       ├── 2.png
│       ├── 3.png
│       ├── 4.png
│       ├── 5.png
│       ├── 6.png
│       ├── 7.png
│       ├── 8.png
│       └── 9.png
├── code
│   ├── IoT
│   │   ├── IoT.py
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   └── local_config.cpython-311.pyc
│   │   ├── cloudcomputing-415100-a9f3f6179657.json
│   │   ├── local_config.py
│   │   └── reader.py
│   ├── __pycache__
│   │   └── message_class.cpython-311.pyc
│   ├── access_server.py
│   ├── node.py
│   ├── p2pnetwork
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-311.pyc
│   │   │   ├── node.cpython-311.pyc
│   │   │   └── nodeconnection.cpython-311.pyc
│   │   ├── node.py
│   │   ├── nodeconnection.py
│   │   └── tests
│   │       ├── __init__.py
│   │       ├── test_node.py
│   │       ├── test_node_compression.py
│   │       └── test_nodeconnection.py
│   └── scripts
│       ├── __pycache__
│       │   └── local_config.cpython-311.pyc
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
