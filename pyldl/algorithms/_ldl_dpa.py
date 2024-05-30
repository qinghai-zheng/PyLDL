import keras
import tensorflow as tf

from scipy.stats import rankdata

from pyldl.algorithms.base import BaseDeepLDL, BaseBFGS


class LDL_DPA(BaseBFGS, BaseDeepLDL):

    @staticmethod
    @tf.function
    def rnkdpa(R, y_pred):
        return -tf.reduce_sum(tf.reduce_mean(R * y_pred, axis=1))

    @staticmethod
    @tf.function
    def disvar(y, y_pred):
        return tf.reduce_sum(
            (tf.math.reduce_variance(y, axis=1) - tf.math.reduce_variance(y_pred, axis=1))**2
        )

    @tf.function
    def _loss(self, params_1d):
        y_pred = keras.activations.softmax(self._X @ self._params2model(params_1d)[0])
        kld = tf.math.reduce_sum(keras.losses.kl_divergence(self._y, y_pred))
        rnkdpa = self.rnkdpa(self._R, y_pred)
        disvar = self.disvar(self._y, y_pred)
        return kld + self._alpha * rnkdpa + self._beta * disvar + self._gamma * self._l2_reg(self._model)

    def _before_train(self):
        self._R = tf.cast(rankdata(self._y, axis=1), tf.float32)

    def fit(self, X, y, alpha=1e-2, beta=1e-2, gamma=1e-6, **kwargs):
        self._alpha = alpha
        self._beta = beta
        self._gamma = gamma
        return super().fit(X, y, **kwargs)
