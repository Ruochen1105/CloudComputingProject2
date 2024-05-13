"""
Communicate with the GCP ML service to get the prediction result
Reference: github.com/googleapis/python-aiplatform/blob/main/samples/snippets/prediction_service/predict_image_classification_sample.py
"""
import base64
from PIL import Image

from google.cloud.aiplatform import Endpoint

import local_config


endpoint = Endpoint(endpoint_name=local_config.endpoint_id, project=local_config.project, location=local_config.location, credentials=)


if __name__ == "__main__":
    im = Image.open("./assets/accidents/0.png")
    im.show()
    endpoint.predict(instances=[])

