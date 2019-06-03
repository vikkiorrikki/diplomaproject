import tensorflow as tf
from PIL import Image
import scipy.misc

tf.enable_eager_execution()

filename = "./test/TH.JPG"
im = Image.open(filename)

img_raw = tf.read_file(filename)
img_tensor = tf.image.decode_jpeg(img_raw, ratio=8)

height, width = img_tensor.shape[0], img_tensor.shape[1]

img_tensor = tf.reshape(img_tensor, [1, height, width, 3])
img_tensor = tf.cast(img_tensor, tf.float32) / 255.0

K = 4
img_resize = tf.image.resize_area(img_tensor, [height // K, width // K])

img_resize = tf.reshape(img_resize, [height // K, width // K, 3])

# noise_level = 0.03
# img_resize = img_resize + tf.random_normal(img_resize.get_shape(), stddev=noise_level)

img = scipy.misc.toimage(img_resize, cmin=0., cmax=1.)
img = img.resize((width*8, height*8), Image.ANTIALIAS)
img.save("./test/blur.jpg", "JPEG")