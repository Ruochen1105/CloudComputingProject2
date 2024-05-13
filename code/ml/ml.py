"""
Communicate with the GCP ML service to get the prediction result
Reference: github.com/googleapis/python-aiplatform/blob/main/samples/snippets/prediction_service/predict_image_classification_sample.py
"""
import os
import base64

from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
from google.oauth2.service_account import Credentials

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


def predict_image_classification_sample(
    project: str = os.getenv("project"),
    endpoint_id: str = os.getenv("endpoint_id"),
    filename: str = "./assets/accidents/0.png",
    location: str = os.getenv("location"),
    api_endpoint: str = os.getenv("api_endpoint"),
):
    # The AI Platform services require regional API endpoints.
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    cred = Credentials.from_service_account_file(os.getenv("cred"))
    client = aiplatform.gapic.PredictionServiceClient(credentials=cred, client_options=client_options)
    with open(filename, "rb") as f:
        file_content = f.read()

    # The format of each instance should conform to the deployed model's prediction input schema.
    encoded_content = base64.b64encode(file_content).decode("utf-8")
    instance = predict.instance.ImageClassificationPredictionInstance(
        content=encoded_content,
    ).to_value()
    instances = [instance]
    # See gs://google-cloud-aiplatform/schema/predict/params/image_classification_1.0.0.yaml for the format of the parameters.
    parameters = predict.params.ImageClassificationPredictionParams(
        confidence_threshold=0.5,
        max_predictions=5,
    ).to_value()
    endpoint = client.endpoint_path(
        project=project, location=location, endpoint=endpoint_id
    )
    response = client.predict(
        endpoint=endpoint, instances=instances, parameters=parameters
    )
    print("response")
    print(" deployed_model_id:", response.deployed_model_id)
    # See gs://google-cloud-aiplatform/schema/predict/prediction/image_classification_1.0.0.yaml for the format of the predictions.
    predictions = response.predictions
    for prediction in predictions:
        print(" prediction:", dict(prediction)["displayNames"][0])


if __name__ == "__main__":
    predict_image_classification_sample()
