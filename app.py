import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
import time
from io import BytesIO

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Replace with your own subscription key and endpoint
subscription_key = "edf2c5b067934029aa7f78c75e601f3e"
endpoint = "https://cvtestings.cognitiveservices.azure.com/"

computervision_client = ComputerVisionClient(
    endpoint, CognitiveServicesCredentials(subscription_key)
)


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/script.js")
def serve_script():
    return send_from_directory(".", "script.js")


@app.route("/extract-text", methods=["POST"])
def extract_text():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    try:
        image = request.files["image"]
        image_data = image.read()
        image_stream = BytesIO(image_data)

        logging.info("Sending image to Azure Cognitive Services")
        read_response = computervision_client.read_in_stream(image_stream, raw=True)
        read_operation_location = read_response.headers["Operation-Location"]
        operation_id = read_operation_location.split("/")[-1]

        logging.info(f"Operation ID: {operation_id}")

        while True:
            read_result = computervision_client.get_read_result(operation_id)
            if read_result.status not in ["notStarted", "running"]:
                break
            time.sleep(1)

        logging.info(f"Read operation status: {read_result.status}")

        extracted_text = []
        if read_result.status == OperationStatusCodes.succeeded:
            for text_result in read_result.analyze_result.read_results:
                for line in text_result.lines:
                    extracted_text.append(line.text)

            logging.info(f"Extracted text: {extracted_text}")
            return jsonify({"text": "\n".join(extracted_text)})
        else:
            logging.error(f"Text extraction failed with status: {read_result.status}")
            return jsonify({"error": "Text extraction failed"}), 500

    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500


if __name__ == "__main__":
    app.run(debug=True)
