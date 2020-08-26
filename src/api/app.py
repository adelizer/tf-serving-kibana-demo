import os
import logging
from cmreslogging.handlers import CMRESHandler
from src.api.constants import *

# configure logger first before doing other imports to make sure the logs are directed to cmres handler
logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(LOGLEVEL)
handler = CMRESHandler(hosts=[{'host': ELASTICSEARCH_URL, 'port': ELASTICSEARCH_PORT}],
                       auth_type=CMRESHandler.AuthType.NO_AUTH,
                       es_index_name=ELASTICSEARCH_INDEX,
                       es_additional_fields={'App': PROJECT_NAME, 'Environment': ENVIRONMENT})
logger.addHandler(handler)


from prometheus_client import multiprocess
from prometheus_client import generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST
from prometheus_client import Counter, Histogram
from flask import Flask
from src.api import settings


flask_app = Flask(__name__)

authentic_counter = Counter('api:class_0', 'Prometheus counter for authentic response')
authentic_counter1 = Counter('api:class_1', 'Prometheus counter for authentic response')

authentic_counter.inc()

def load_uploaded_file():
    """Read the first uploaded file and returns it as an OpenCV image."""
    # Default value of image.
    img = None
    if request.files:
        for item in request.files.items():
            # name of the form field used for uploading
            fieldname = item[0]
            file = request.files[fieldname]
            # First decode and load using OpenCV
            byte_array = np.array(bytearray(file.read()), dtype=np.uint8)
            img = cv2.imdecode(byte_array, cv2.IMREAD_COLOR)
            # Finally preprocess the image
            img = preprocess_image(img)
            # accept one file only
            break
    return img


def preprocess_image(image):
    """Preprocess an image with OpenCV according to how the model was trained.

    Args:
        image(str): The loaded image.

    Returns:
        the preprocessed image.

    """
    # Resize image.
    image = cv2.resize(image, (NETWORK_WIDTH, NETWORK_HEIGHT))
    # Cast to float
    image = image.astype(np.float32)
    return image


def call_tf_serving(img):
    """Do a request on internal port of tensorflow/serving.

    Args:
        img(np.array): The image array.

    Returns:
        the Flask Response object containing the status and answer.

    """
    model_name = os.environ['MODEL_NAME']
    headers = {"content-type": "application/json"}
    data = json.dumps({"signature_name": "serving_default", "instances": [img.tolist()]})
    tf_infer_url = 'http://localhost:{}/v1/models/{}:predict'.format(TF_SERVE_PORT, model_name)
    try:
        r = requests.post(tf_infer_url, data=data, headers=headers)
        resp = Response(r.text, status=r.status_code,
                        mimetype=r.headers.get('Content-Type'))
    except requests.ConnectionError:
        error_message = 'Could not connect to {}'.format(tf_infer_url)
        resp = Response(error_message, status=500, mimetype='text/plain')
    return resp


@flask_app.route('/debug_img', methods=['POST'])
def debug_img():
    """Debugging endpoint to make sure everytjing is correct.

    Applies all the pre-processing we'd apply to the image before feeding the
    image to the model, and returns the image as `png`. Allows you to see the result
    of the pre-processing aplied & check if everything looks fine.

    """
    img = load_uploaded_file()
    _, buffer = cv2.imencode('.png', img)
    return Response(buffer.tobytes(), mimetype='image/png')


@flask_app.route('/meta', methods=['GET'])
def meta():
    """Metadata url endpoint."""
    model_name = os.environ['MODEL_NAME']
    tf_meta_url = "http://localhost:{}/v1/models/{}/metadata".format(TF_SERVE_PORT, model_name)
    try:
        r = requests.get(tf_meta_url)
        resp = Response(r.text, status=r.status_code,
                        mimetype=r.headers.get('Content-Type'))
    except requests.ConnectionError:
        error_message = 'Could not connect to {}\n'.format(tf_meta_url)
        resp = Response(error_message, status=500, mimetype='text/plain')

    return resp


@flask_app.route('/infer', methods=['POST'])
def infer():
    """Inference (prediction) endpoint.

    Will load the image from the `request` object, preprocess it and serve it to the
    `tensorflow/serving` port & endpoint.

    Thus we avoid calling tensorflow-serving directly.

    """
    img = load_uploaded_file()
    return call_tf_serving(img)


@flask_app.route("/metrics")
def metrics():
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    data = generate_latest(registry)
    status = '200 OK'
    response_headers = [
        ('Content-type', CONTENT_TYPE_LATEST),
        ('Content-Length', str(len(data)))
    ]
    return data


if __name__ == "__main__":
    flask_app.run(debug=settings.FLASK_DEBUG)
