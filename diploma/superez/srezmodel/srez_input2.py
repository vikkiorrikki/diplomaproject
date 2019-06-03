import tensorflow as tf

def setup_inputs(sess, filenames, image_size=None, capacity_factor=3):

    filename = filenames[0]
    
    # Read each JPEG file
    img_raw = tf.read_file(filename)
    image = tf.image.decode_jpeg(img_raw)

    height, width = tf.shape(image)[0], tf.shape(image)[1]

    image = tf.cast(image, tf.float32) / 255.0

    feature = tf.reshape(image, [height, width, 3])

    features =  tf.convert_to_tensor([feature])

    return features