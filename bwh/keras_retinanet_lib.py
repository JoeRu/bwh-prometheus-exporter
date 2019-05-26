import tkinter
# import keras
import keras

# import keras_retinanet
from keras_retinanet import models
from keras_retinanet.utils.image import read_image_bgr, preprocess_image, resize_image
from keras_retinanet.utils.visualization import draw_box, draw_caption
from keras_retinanet.utils.colors import label_color

# import miscellaneous modules
import matplotlib.pyplot as plt
import cv2
import os
import numpy as np
import time
# set tf backend to allow memory to grow, instead of claiming everything
import tensorflow as tf

import logging

#-------------Output Logger
# create logger
logger = logging.getLogger(os.path.basename(__file__))
#logger.setLevel(logging.INFO)
logger.setLevel(logging.INFO)
# create console handler with a higher log level
ch = logging.StreamHandler()
#ch.setLevel(logging.INFO)
ch.setLevel(logging.INFO)

# create file handler which logs even debug messages
fh = logging.FileHandler(os.path.basename(__file__)+'.log')
fh.setLevel(logging.ERROR)

# create formatter and add it to the handlers
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('%(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)
#-------------Output Logger

# load label to names mapping for visualization purposes
labels_to_names = {0: 'bee', 1: 'wasp', 2: 'hornet'}


def get_session():
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    return tf.Session(config=config)

# use this environment flag to change which GPU to use
#os.environ["CUDA_VISIBLE_DEVICES"] = "1"


keras.backend.tensorflow_backend.set_session(get_session())
model_path = 'cfg/bwh_model.h5'
# load retinanet model
bwh_model = models.load_model(model_path, backbone_name='resnet50')
logger.debug(bwh_model)
graph = tf.get_default_graph()

def performDetect(imagePath="test.jpg", output="output.jpg", thresh= 0.81):
    """
    """
    # load image
    image = read_image_bgr(imagePath)

    # copy to draw on
    draw = image.copy()
    draw = cv2.cvtColor(draw, cv2.COLOR_BGR2RGB)

    # preprocess image for network
    image = preprocess_image(image)
    image, scale = resize_image(image)

    # process image
    start = time.time()
    with graph.as_default():
        boxes, scores, labels = bwh_model.predict_on_batch(np.expand_dims(image, axis=0))
    logger.debug("processing time: {}".format( time.time() - start))

    # correct for image scale
    boxes /= scale

    result = zip(boxes[0], scores[0], labels[0])
    resultlist = list(result)
    bees = []
    wasps = []
    hornets = []
    result_objects = {
        0: bees,
        1: wasps,
        2: hornets
    }
    logger.info("Actual run found:")
    for box, score, label in zip(boxes[0], scores[0], labels[0]):
        # scores are sorted so we can break
        if score < thresh:
            break

        color = label_color(label)

        b = box.astype(int)
        draw_box(draw, b, color=color)

        caption = "{} {:.3f}".format(labels_to_names[label], score)
        draw_caption(draw, b, caption)

        tuple = (score, box)
        (result_objects.get(label)).append(tuple)
        logger.info("found {} {}%".format(labels_to_names.get(label),str(np.rint(100 * score))))

    draw2 = draw.copy()
    draw2 = cv2.cvtColor(draw, cv2.COLOR_RGB2BGR)

    cv2.imwrite(output, draw2)
    return result_objects
