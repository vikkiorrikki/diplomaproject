import sys

sys.path.insert(0, 'D:\\wamp64\\www\\diploma\\superez')
sys.path.insert(0, 'D:\\wamp64\\www\\diploma\\superez\srezmodel')

import superez.srezmodel.srez_input2 as srez_input
import superez.srezmodel.srez_model2 as srez_model

import os.path
import random
import ntpath
import numpy as np
import numpy.random
import scipy.misc

import tensorflow as tf

from django.conf import settings

FLAGS = tf.app.flags.FLAGS

# Configuration (alphabetically)
tf.app.flags.DEFINE_integer('batch_size', 1,
                            "Number of samples per batch.")

tf.app.flags.DEFINE_string('dataset', 'test',
                           "Path to the dataset directory.")

tf.app.flags.DEFINE_string('checkpoint_dir', os.path.join(settings.BASE_DIR, "superez/srezmodel/checkpoint"),
                           "Output folder where checkpoints are dumped.")

tf.app.flags.DEFINE_bool('log_device_placement', False,
                         "Log the device where variables are placed.")

tf.app.flags.DEFINE_integer('random_seed', 0,
                            "Seed used to initialize rng.")


def setup_tensorflow():
    # Create session
    config = tf.ConfigProto(log_device_placement=FLAGS.log_device_placement)
    config.gpu_options.allow_growth = True  # to avoid GPU memory errors
    sess = tf.Session(config=config)

    # Initialize rng with a deterministic seed
    with sess.graph.as_default():
        tf.set_random_seed(FLAGS.random_seed)

    random.seed(FLAGS.random_seed)
    np.random.seed(FLAGS.random_seed)

    # summary_writer = tf.train.SummaryWriter(FLAGS.train_dir, sess.graph)

    return sess, None


def inference(path_to_file):
    # Load checkpoint
    if not tf.gfile.IsDirectory(FLAGS.checkpoint_dir):
        raise FileNotFoundError("Could not find folder `%s'" % (FLAGS.checkpoint_dir,))

    # Setup global tensorflow state
    sess, summary_writer = setup_tensorflow()

    # Prepare directories
    filenames = [path_to_file]

    # Setup async input queues
    features = srez_input.setup_inputs(sess, filenames, 128)

    # Create and initialize model
    [gene_minput, gene_moutput] = srez_model.create_model(sess, features)

    # Restore variables from checkpoint
    saver = tf.train.Saver()
    filename = 'checkpoint_new.txt'
    filename = os.path.join(FLAGS.checkpoint_dir, filename)
    saver.restore(sess, filename)

    # test_feature, test_label = sess.run([features, labels])
    test_feature = sess.run(features)

    # Show progress with test features
    gene_output = sess.run(gene_moutput, feed_dict={gene_minput: test_feature})

    # Visualize
    max_samples = 1

    size = [test_feature.shape[1], test_feature.shape[2]]

    nearest = tf.image.resize_nearest_neighbor(test_feature, size)
    nearest = tf.maximum(tf.minimum(nearest, 1.0), 0.0)

    gene_output = tf.image.resize_nearest_neighbor(gene_output, size)
    clipped = tf.maximum(tf.minimum(gene_output, 1.0), 0.0)

    # image   = tf.concat([nearest, clipped, test_label], 2)
    image = tf.concat([clipped], 2)

    image = image[0:max_samples, :, :, :]
    image = tf.concat([image[i, :, :, :] for i in range(max_samples)], 0)
    image = sess.run(image)

    imgname = "restored_" + ntpath.basename(filenames[0])
    scipy.misc.toimage(image, cmin=0., cmax=1.).save(os.path.join(ntpath.dirname(filenames[0]), imgname))
    print("    Saved %s" % (imgname,))


if __name__ == "__main__":
    inference("./test/000621.jpg")
