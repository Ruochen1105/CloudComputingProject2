# CloudComputingProject2

Final project for NYU Courant Spring 2024 course Cloud Computing CICI-GA 3033-010 by Ruochen Miao rm5327 and Chengying Wang cw4450.

## Traffic Accident Sharing

This repo is a traffic accident sharing application built on a P2P network. Node joins the network through an access server. The first node joining the network becomes the master node, and assigns {[I]oT, [M]L, [A]R} roles to incoming nodes, which then become service nodes.

Every node can leave at any time. When a service node leaves, the master node updates its internal records; and when the master node leaves, it assigns a new node to be the master node as well as updates the record in the access server, unless it is the last node in the network, in which case it simply quits and tells the access server to erase its record.

The IoT node simulates an IoT device registered on Azure IoT Hub. It continuously reads street view images from local storage, uploads the images to Google Cloud Storage (which gives back an URL to the stored image), and pushes the URL together with the simulated longitude and latitude to the Azure IoT Hub.

The ML node subscribes to the event hub of the Azure IoT Hub. Whenever it gets a telemetry from the event hub, the ML node retrieves the image from Google Cloud Storage using the URL and feeds the image to the image classification model hosted on Google Vertex AI. The ML node will get a prediction result (accident v.s. no_accident) from the cloud, and inserts the prediction together with the URL, longitude, and latitude (from the telemetry) into AWS RDS, relational database served by AWS.

The AR node answers the request for checking the accident records from nodes in the network. Requests from IoT nodes and ML nodes are routed by the master node, while the master node sends its request to AR nodes directly and AR nodes serve their own requests. AR nodes retrieves the (latest five in the case of this project) rows from AWS RDS and uses AR technologies to render these rows into 3D text models. The AR is planned to be implemented using Azure Remote Rendering, but it is postponed due to limited time and experience with Unity and AR.

## File Structure

```bash
.
├── README.md
├── assets
│   ├── accidents
│   └── no_accidents
├── code
│   ├── access_server.py
│   ├── db
│   │   ├── __init__.py
│   │   └── db.py
│   ├── .env
│   ├── iot
│   │   ├── __init__.py
│   │   ├── iot.py
│   │   └── reader.py
│   ├── ml
│   │   ├── __init__.py
│   │   └── ml.py
│   ├── node.py
│   ├── p2pnetwork
│   │   ├── __init__.py
│   │   ├── node.py
│   │   ├── nodeconnection.py
│   │   └── tests
│   │       ├── __init__.py
│   │       ├── test_node.py
│   │       ├── test_node_compression.py
│   │       └── test_nodeconnection.py
│   └── scripts
│       ├── local_config.py
│       └── sampling.py
└── requirements.txt
```

## Dataset

The images without accidents are from [Traffic Detection Project](https://www.kaggle.com/datasets/yusufberksardoan/traffic-detection-project/data).

The images with accidents are from [Vehicle Crash Dataset Computer Vision Project](https://universe.roboflow.com/object-detection-3iugc/vehicle-crash-dataset).

These two datasets are sharing the following YOLOv8 file structure, except that "Vehicle Crash Dataset Computer Vision Project" does not have "valid" and "test":
```
.
├── ...              # meta info
├── test
│   ├── labels       # not used
│   └── images
│       ├── ...
│       └── {image_name}.jpg
├── trian
│   └── ...
└── valid
    └── ...
```

The dataset used in this project is randomly sampled from all images of the two public datasets. The script used is `./code/scripts/sampling.py`.

## .env
```bash
# IoT
wd = "" # for reading local images
CONNECTION_STRING = "" # device on IoT Hub
connection_str = "" # event hub

# Google Cloud Storage
path_to_cred = "" # path to the GCP json key of service roles
bucket_name = ""

# Google Vertex AI
project = "" # project id
endpoint_id = ""
location = ""
api_endpoint = ""
cred = "" # path to the GCP json key of service roles

# AWS RDS
host = ""
port = 3306
user = ""
password = ""
database = ""
```

## requirements.txt

Libraries used in this project. The latest versions at the time of this project are used.

## References

### P2P Framework

[python-p2p-network](https://github.com/macsnoeren/python-p2p-network)

### gitignore

[A collection of .gitignore templates](https://github.com/github/gitignore)

### IoT

[Azure IoT Samples for Python](github.com/Azure-Samples/azure-iot-samples-python/blob/master/iot-hub/Quickstarts/simulated-device/SimulatedDeviceSync.py)

### ML

[Vertex AI SDK for Python](github.com/googleapis/python-aiplatform/blob/main/samples/snippets/prediction_service/predict_image_classification_sample.py)
