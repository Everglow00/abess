import warnings
import numpy as np
from sklearn.metrics import r2_score, d2_tweedie_score, ndcg_score
from .metrics import concordance_index_censored
from .bess_base import bess_base
from .utilities import new_data_check
from .functions import (BreslowEstimator)
# from .nonparametric import _compute_counts


def fix_docs(cls):
    # This function is to inherit the docstring from base class
    # and avoid unnecessary duplications on description.
    index = cls.__doc__.find("Examples\n    --------\n")
    if index != -1:
        cls.__doc__ = cls.__doc__[:index] + \
            cls.__bases__[0].__doc__ + cls.__doc__[index:]
    return cls


@ fix_docs
class LogisticRegression(bess_base):
    r"""
    Adaptive Best-Subset Selection (ABESS) algorithm for logistic regression.

    Parameters
    ----------
    splicing_type: {0, 1}, optional, default=0
        The type of splicing:
        "0" for decreasing by half, "1" for decresing by one.
    important_search : int, optional, default=128
        The size of inactive set during updating active set when splicing.
        It should be a non-positive integer and if important_search=0,
        it would be set as the size of whole inactive set.

    Examples
    --------
    >>> ### Sparsity known
    >>>
    >>> from abess.linear import LogisticRegression
    >>> from abess.datasets import make_glm_data
    >>> import numpy as np
    >>> np.random.seed(12345)
    >>> data = make_glm_data(n = 100, p = 50, k = 10, family = 'binomial')
    >>> model = LogisticRegression(support_size = 10)
    >>> model.fit(data.x, data.y)
    LogisticRegression(always_select=[], support_size=10)
    >>> model.predict(data.x)[1:10]
    array([0., 0., 1., 1., 0., 1., 0., 1., 0.])

    >>> ### Sparsity unknown
    >>>
    >>> # path_type="seq"
    >>> model = LogisticRegression(path_type = "seq")
    >>> model.fit(data.x, data.y)
    LogisticRegression(always_select=[])
    >>> model.predict(data.x)[1:10]
    array([0., 1., 0., 0., 1., 0., 1., 0., 1., 1.])
    >>>
    >>> # path_type="gs"
    >>> model = LogisticRegression(path_type="gs")
    >>> model.fit(data.x, data.y)
    LogisticRegression(always_select=[], path_type='gs')
    >>> model.predict(data.x)[1:10]
    array([0., 0., 0., 1., 1., 0., 1., 0., 1., 0.])
    """

    def __init__(self, max_iter=20, exchange_num=5, path_type="seq",
                 is_warm_start=True, support_size=None, alpha=None,
                 s_min=None, s_max=None,
                 ic_type="ebic", ic_coef=1.0, cv=1, screening_size=-1,
                 always_select=None,
                 primary_model_fit_max_iter=10, primary_model_fit_epsilon=1e-8,
                 approximate_Newton=False,
                 thread=1,
                 sparse_matrix=False,
                 splicing_type=0,
                 important_search=128,
                 ):
        super().__init__(
            algorithm_type="abess", model_type="Logistic", normalize_type=2,
            path_type=path_type, max_iter=max_iter, exchange_num=exchange_num,
            is_warm_start=is_warm_start, support_size=support_size,
            alpha=alpha, s_min=s_min, s_max=s_max,
            ic_type=ic_type, ic_coef=ic_coef, cv=cv,
            screening_size=screening_size,
            always_select=always_select,
            primary_model_fit_max_iter=primary_model_fit_max_iter,
            primary_model_fit_epsilon=primary_model_fit_epsilon,
            approximate_Newton=approximate_Newton,
            thread=thread,
            sparse_matrix=sparse_matrix,
            splicing_type=splicing_type,
            important_search=important_search,
            _estimator_type='classifier'
        )

    def _more_tags(self):
        return {'binary_only': True,
                'no_validation': True}

    def predict_proba(self, X):
        r"""
        Give the probabilities of new sample
        being assigned to different classes.

        Parameters
        ----------
        X : array-like, shape(n_samples, p_features)
            Sample matrix to be predicted.

        Returns
        -------
        proba : array-like, shape(n_samples, 2)
            Returns the probabilities for class "0" and "1"
            on given X.
        """
        X = new_data_check(self, X)

        intercept_ = np.ones(X.shape[0]) * self.intercept_
        xbeta = X.dot(self.coef_) + intercept_
        proba = np.exp(xbeta) / (1 + np.exp(xbeta))
        return np.vstack((np.ones(X.shape[0]) - proba, proba)).T

    def predict(self, X):
        r"""
        This function predicts class label for given data.

        Parameters
        ----------
        X : array-like, shape(n_samples, p_features)
            Sample matrix to be predicted.

        Returns
        -------
        y : array-like, shape(n_samples,)
            Predict class labels (0 or 1) for samples in X.
        """
        X = new_data_check(self, X)

        intercept_ = np.ones(X.shape[0]) * self.intercept_
        xbeta = X.dot(self.coef_) + intercept_
        y = np.repeat(self.classes_[0], xbeta.size)
        if self.classes_.size == 2:
            y[xbeta > 0] = self.classes_[1]
        return y

    def score(self, X, y):
        r"""
        Give new data, and it returns the prediction accuracy.

        Parameters
        ----------
        X : array-like, shape(n_samples, p_features)
            Sample matrix.
        y : array-like, shape(n_samples,)
            Real class labels (0 or 1) for X.

        Returns
        -------
        score : float
            The mean prediction accuracy on the given data.
        """
        X, y = new_data_check(self, X, y)

        # intercept_ = np.ones(X.shape[0]) * self.intercept_
        # xbeta = X.dot(self.coef_) + intercept_
        # xbeta[xbeta > 30] = 30
        # xbeta[xbeta < -30] = -30
        # pr = np.exp(xbeta) / (1 + np.exp(xbeta))
        # return (y * np.log(pr) +
        #         (np.ones(X.shape[0]) - y) *
        #         np.log(np.ones(X.shape[0]) - pr)).sum()
        y_pred = self.predict(X)
        return (y == y_pred).mean()


@ fix_docs
class LinearRegression(bess_base):
    r"""
    Adaptive Best-Subset Selection(ABESS) algorithm for linear regression.

    Parameters
    ----------
    splicing_type: {0, 1}, optional, default=0
        The type of splicing:
        "0" for decreasing by half, "1" for decresing by one.
    important_search : int, optional, default=128
        The size of inactive set during updating active set when splicing.
        It should be a non-positive integer and if important_search=0,
        it would be set as the size of whole inactive set.

    Examples
    --------
    >>> ### Sparsity known
    >>>
    >>> from abess.linear import LinearRegression
    >>> from abess.datasets import make_glm_data
    >>> import numpy as np
    >>> np.random.seed(12345)
    >>> data = make_glm_data(n = 100, p = 50, k = 10, family = 'gaussian')
    >>> model = LinearRegression(support_size = 10)
    >>> model.fit(data.x, data.y)
    LinearRegression(always_select=[], support_size=10)
    >>> model.predict(data.x)
    array([   1.42163813,  -43.23929886, -139.79509191,  141.45138403])

    >>> ### Sparsity unknown
    >>>
    >>> # path_type="seq"
    >>> model = LinearRegression(path_type = "seq")
    >>> model.fit(data.x, data.y)
    LinearRegression(always_select=[])
    >>> model.predict(data.x)[1:4]
    array([   1.42163813,  -43.23929886, -139.79509191,  141.45138403])
    >>>
    >>> # path_type="gs"
    >>> model = LinearRegression(path_type="gs")
    >>> model.fit(data.x, data.y)
    LinearRegression(always_select=[], path_type='gs')
    >>> model.predict(data.x)[1:4]
    array([   1.42163813,  -43.23929886, -139.79509191,  141.45138403])
    """

    def __init__(self, max_iter=20, exchange_num=5, path_type="seq",
                 is_warm_start=True, support_size=None,
                 alpha=None, s_min=None, s_max=None,
                 ic_type="ebic", ic_coef=1.0, cv=1, screening_size=-1,
                 always_select=None,
                 thread=1, covariance_update=False,
                 sparse_matrix=False,
                 splicing_type=0,
                 important_search=128,
                 # primary_model_fit_max_iter=10,
                 # primary_model_fit_epsilon=1e-8,
                 # approximate_Newton=False
                 ):
        super().__init__(
            algorithm_type="abess", model_type="Lm", normalize_type=1,
            path_type=path_type, max_iter=max_iter, exchange_num=exchange_num,
            is_warm_start=is_warm_start, support_size=support_size,
            alpha=alpha, s_min=s_min, s_max=s_max,
            ic_type=ic_type, ic_coef=ic_coef, cv=cv,
            screening_size=screening_size,
            always_select=always_select,
            thread=thread, covariance_update=covariance_update,
            sparse_matrix=sparse_matrix,
            splicing_type=splicing_type,
            important_search=important_search,
            _estimator_type='regressor'
        )

    def _more_tags(self):
        return {'multioutput': False}

    def predict(self, X):
        r"""
        Predict on given data.

        Parameters
        ----------
        X : array-like, shape(n_samples, p_features)
            Sample matrix to be predicted.

        Returns
        -------
        y : array-like, shape(n_samples,)
            Prediction of the mean on given X.
        """
        X = new_data_check(self, X)

        intercept_ = np.ones(X.shape[0]) * self.intercept_
        return X.dot(self.coef_) + intercept_

    def score(self, X, y):
        r"""
        Give data, and it returns the coefficient of determination.

        Parameters
        ----------
        X : array-like, shape(n_samples, p_features)
            Sample matrix.
        y : array-like, shape(n_samples, p_features)
            Real response for given X.

        Returns
        -------
        score : float
            :math:`R^2` score.
        """
        X, y = new_data_check(self, X, y)
        y_pred = self.predict(X)
        # return ((y - y_pred) * (y - y_pred)).sum()
        return r2_score(y, y_pred)


@ fix_docs
class CoxPHSurvivalAnalysis(bess_base, BreslowEstimator):
    r"""
    Adaptive Best-Subset Selection (ABESS) algorithm for
    Cox proportional hazards model.

    Parameters
    ----------
    splicing_type: {0, 1}, optional, default=0
        The type of splicing:
        "0" for decreasing by half, "1" for decresing by one.
    important_search : int, optional, default=128
        The size of inactive set during updating active set when splicing.
        It should be a non-positive integer and if important_search=0,
        it would be set as the size of whole inactive set.

    Examples
    --------
    >>> ### Sparsity known
    >>>
    >>> from abess.linear import CoxPHSurvivalAnalysis
    >>> from abess.datasets import make_glm_data
    >>> import numpy as np
    >>> np.random.seed(12345)
    >>> data = make_glm_data(n = 100, p = 50, k = 10, family = 'cox')
    censoring rate:0.65
    >>> model = CoxPHSurvivalAnalysis(support_size = 10)
    >>> model.fit(data.x, data.y)
    CoxPHSurvivalAnalysis(always_select=[], support_size=10)
    >>> model.predict(data.x)[1:4]
    array([1.08176927e+00, 6.37029117e-04, 3.64112556e-06, 4.09523406e+05])

    >>> ### Sparsity unknown
    >>>
    >>> # path_type="seq"
    >>> model = CoxPHSurvivalAnalysis(path_type = "seq")
    >>> model.fit(data.x, data.y)
    CoxPHSurvivalAnalysis(always_select=[], support_size=10)
    >>> model.predict(data.x)[1:4]
    array([1.08176927e+00, 6.37029117e-04, 3.64112556e-06, 4.09523406e+05])
    >>>
    >>> # path_type="gs"
    >>> model = CoxPHSurvivalAnalysis(path_type="gs")
    >>> model.fit(data.x, data.y)
    CoxPHSurvivalAnalysis(always_select=[], path_type='gs')
    >>> model.predict(data.x)[1:4]
    array([1.07629689e+00, 6.47263126e-04, 4.30660826e-06, 3.66389638e+05])
    """

    def __init__(self, max_iter=20, exchange_num=5, path_type="seq",
                 is_warm_start=True, support_size=None,
                 alpha=None, s_min=None, s_max=None,
                 ic_type="ebic", ic_coef=1.0, cv=1, screening_size=-1,
                 always_select=None,
                 primary_model_fit_max_iter=10, primary_model_fit_epsilon=1e-8,
                 approximate_Newton=False,
                 thread=1,
                 sparse_matrix=False,
                 splicing_type=0,
                 important_search=128
                 ):
        super().__init__(
            algorithm_type="abess", model_type="Cox", normalize_type=3,
            path_type=path_type, max_iter=max_iter, exchange_num=exchange_num,
            is_warm_start=is_warm_start, support_size=support_size,
            alpha=alpha, s_min=s_min, s_max=s_max,
            ic_type=ic_type, ic_coef=ic_coef, cv=cv,
            screening_size=screening_size,
            always_select=always_select,
            primary_model_fit_max_iter=primary_model_fit_max_iter,
            primary_model_fit_epsilon=primary_model_fit_epsilon,
            approximate_Newton=approximate_Newton,
            thread=thread,
            sparse_matrix=sparse_matrix,
            splicing_type=splicing_type,
            important_search=important_search,
            baseline_model=BreslowEstimator()
        )

    def _more_tags(self):
        # Note: We ignore estimator's check here because it would pass
        # an 1-column `y` for testing, but for `CoxPHSurvivalAnalysis()`,
        # 2-column `y` should be given (one for time, another for censoring).
        return {'_skip_test': True}

    def predict(self, X):
        r"""
        Returns the time-independent part of hazard function,
        i.e. :math:`\exp(X\beta)` on given data.

        Parameters
        ----------
        X : array-like, shape(n_samples, p_features)
            Sample matrix to be predicted.

        Returns
        -------
        y : array-like, shape(n_samples,)
            Return :math:`\exp(X\beta)`.
        """
        X = new_data_check(self, X)

        return np.exp(X.dot(self.coef_))

    def score(self, X, y):
        r"""
        Give data, and it returns C-index.

        Parameters
        ----------
        X : array-like, shape(n_samples, p_features)
            Sample matrix.
        y : array-like, shape(n_samples, p_features)
            Real response for given X.

        Returns
        -------
        score : float
            C-index.
        """
        X, y = new_data_check(self, X, y)
        risk_score = X.dot(self.coef_)
        y = np.array(y)
        result = concordance_index_censored(
            np.array(y[:, 1], np.bool_), y[:, 0], risk_score)
        return result[0]

    def predict_survival_function(self, X):
        r"""
        Predict survival function.
        The survival function for an individual
        with feature vector :math:`x` is defined as

        .. math::
            S(t \mid x) = S_0(t)^{\exp(x^\top \beta)} ,

        where :math:`S_0(t)` is the baseline survival function,
        estimated by Breslow's estimator.

        Parameters
        ----------
        X : array-like, shape = (n_samples, n_features)
            Data matrix.

        Returns
        -------
        survival : ndarray of :class:`StepFunction`, shape = (n_samples,)
            Predicted survival functions.
        """
        return self.baseline_model.get_survival_function(
            np.log(self.predict(X)))


@ fix_docs
class PoissonRegression(bess_base):
    r"""
    Adaptive Best-Subset Selection(ABESS) algorithm for Poisson regression.

    Parameters
    ----------
    splicing_type: {0, 1}, optional, default=0
        The type of splicing:
        "0" for decreasing by half, "1" for decresing by one.
    important_search : int, optional, default=128
        The size of inactive set during updating active set when splicing.
        It should be a non-positive integer and if important_search=0,
        it would be set as the size of whole inactive set.

    Examples
    --------
    >>> ### Sparsity known
    >>>
    >>> from abess.linear import PoissonRegression
    >>> from abess.datasets import make_glm_data
    >>> import numpy as np
    >>> np.random.seed(12345)
    >>> data = make_glm_data(n = 100, p = 50, k = 10, family = 'poisson')
    >>> model = PoissonRegression(support_size = 10)
    >>> model.fit(data.x, data.y)
    PoissonRegression(always_select=[], support_size=10)
    >>> model.predict(data.x)[1:4]
    array([1.06757251e+00, 8.92711312e-01, 5.64414159e-01, 1.35820866e+00])

    >>> ### Sparsity unknown
    >>>
    >>> # path_type="seq"
    >>> model = PoissonRegression(path_type = "seq")
    >>> model.fit(data.x, data.y)
    PoissonRegression(always_select=[])
    >>> model.predict(data.x)[1:4]
    array([1.03373139e+00, 4.32229653e-01, 4.48811009e-01, 2.27170366e+00])
    >>>
    >>> # path_type="gs"
    >>> model = PoissonRegression(path_type="gs")
    >>> model.fit(data.x, data.y)
    PoissonRegression(always_select=[], path_type='gs')
    >>> model.predict(data.x)[1:4]
    array([1.03373139e+00, 4.32229653e-01, 4.48811009e-01, 2.27170366e+00])
    """

    def __init__(self, max_iter=20, exchange_num=5, path_type="seq",
                 is_warm_start=True, support_size=None,
                 alpha=None, s_min=None, s_max=None,
                 ic_type="ebic", ic_coef=1.0, cv=1, screening_size=-1,
                 always_select=None,
                 primary_model_fit_max_iter=10, primary_model_fit_epsilon=1e-8,
                 thread=1,
                 sparse_matrix=False,
                 splicing_type=0,
                 important_search=128
                 ):
        super().__init__(
            algorithm_type="abess", model_type="Poisson", normalize_type=2,
            path_type=path_type, max_iter=max_iter, exchange_num=exchange_num,
            is_warm_start=is_warm_start, support_size=support_size,
            alpha=alpha, s_min=s_min, s_max=s_max,
            ic_type=ic_type, ic_coef=ic_coef, cv=cv,
            screening_size=screening_size,
            always_select=always_select,
            primary_model_fit_max_iter=primary_model_fit_max_iter,
            primary_model_fit_epsilon=primary_model_fit_epsilon,
            thread=thread,
            sparse_matrix=sparse_matrix,
            splicing_type=splicing_type,
            important_search=important_search,
            _estimator_type='regressor'
        )

    def _more_tags(self):
        return {"poor_score": True}

    def predict(self, X):
        r"""
        Predict on given data.

        Parameters
        ----------
        X : array-like, shape(n_samples, p_features)
            Sample matrix to be predicted.

        Returns
        -------
        y : array-like, shape(n_samples,)
            Prediction of the mean on X.
        """
        X = new_data_check(self, X)

        intercept_ = np.ones(X.shape[0]) * self.intercept_
        xbeta_exp = np.exp(X.dot(self.coef_) + intercept_)
        return xbeta_exp

    def score(self, X, y):
        r"""
        Give new data, and it returns the :math:`D^2` score.

        Parameters
        ----------
        X : array-like, shape(n_samples, p_features)
            Sample matrix.
        y : array-like, shape(n_samples, p_features)
            Real response for given X.

        Returns
        -------
        score : float
            :math:`D^2` score.
        """
        X, y = new_data_check(self, X, y)

        # intercept_ = np.ones(X.shape[0]) * self.intercept_
        # eta = X.dot(self.coef_) + intercept_
        # exp_eta = np.exp(eta)
        # return (y * eta - exp_eta).sum()
        y_pred = self.predict(X)
        return d2_tweedie_score(y, y_pred, power=1)


@ fix_docs
class MultiTaskRegression(bess_base):
    r"""
    Adaptive Best-Subset Selection(ABESS) algorithm for multitasklearning.

    Parameters
    ----------
    splicing_type: {0, 1}, optional, default=0
        The type of splicing:
        "0" for decreasing by half, "1" for decresing by one.
    important_search : int, optional, default=128
        The size of inactive set during updating active set when splicing.
        It should be a non-positive integer and if important_search=0,
        it would be set as the size of whole inactive set.

    Examples
    --------
    >>> ### Sparsity known
    >>>
    >>> from abess.linear import MultiTaskRegression
    >>> from abess.datasets import make_multivariate_glm_data
    >>> import numpy as np
    >>> np.random.seed(12345)
    >>> data = make_multivariate_glm_data(
    >>>     n = 100, p = 50, k = 10, M = 3, family = 'multigaussian')
    >>> model = MultiTaskRegression(support_size = 10)
    >>> model.fit(data.x, data.y)
    MultiTaskRegression(always_select=[], support_size=10)
    >>> model.predict(data.x)[1:5, ]
    array([[1., 0., 0.],
       [0., 0., 1.],
       [1., 0., 0.],
       [1., 0., 0.],
       [0., 0., 1.]])

    >>> ### Sparsity unknown
    >>>
    >>> # path_type="seq"
    >>> model = MultiTaskRegression(path_type = "seq")
    >>> model.fit(data.x, data.y)
    MultiTaskRegression(always_select=[])
    >>> model.predict(data.x)[1:5, ]
    array([[1., 0., 0.],
       [0., 0., 1.],
       [1., 0., 0.],
       [1., 0., 0.],
       [0., 0., 1.]])
    >>>
    >>> # path_type="gs"
    >>> model = MultiTaskRegression(path_type="gs")
    >>> model.fit(data.x, data.y)
    MultiTaskRegression(always_select=[], path_type='gs')
    >>> model.predict(data.x)[1:5, ]
    array([[1., 0., 0.],
       [0., 0., 1.],
       [1., 0., 0.],
       [1., 0., 0.],
       [0., 0., 1.]])
    """

    def __init__(self, max_iter=20, exchange_num=5, path_type="seq",
                 is_warm_start=True, support_size=None,
                 alpha=None, s_min=None, s_max=None,
                 ic_type="ebic", ic_coef=1.0, cv=1, screening_size=-1,
                 always_select=None,
                 thread=1, covariance_update=False,
                 sparse_matrix=False,
                 splicing_type=0,
                 important_search=128
                 ):
        super().__init__(
            algorithm_type="abess", model_type="Multigaussian",
            normalize_type=1, path_type=path_type,
            max_iter=max_iter, exchange_num=exchange_num,
            is_warm_start=is_warm_start, support_size=support_size,
            alpha=alpha, s_min=s_min, s_max=s_max,
            ic_type=ic_type, ic_coef=ic_coef, cv=cv,
            screening_size=screening_size,
            always_select=always_select,
            thread=thread, covariance_update=covariance_update,
            sparse_matrix=sparse_matrix,
            splicing_type=splicing_type,
            important_search=important_search,
            _estimator_type='regressor'
        )

    def _more_tags(self):
        return {'multioutput': True,
                'multioutput_only': True}

    def predict(self, X):
        r"""
        Prediction of the mean of each response on given data.

        Parameters
        ----------
        X : array-like, shape(n_samples, p_features)
            Sample matrix to be predicted.

        Returns
        -------
        y : array-like, shape(n_samples, M_responses)
            Prediction of the mean of each response on given X.
            Each column indicates one response.
        """
        X = new_data_check(self, X)

        intercept_ = np.repeat(
            self.intercept_[np.newaxis, ...], X.shape[0], axis=0)
        y_pred = X.dot(self.coef_) + intercept_
        if len(y_pred.shape) == 1:
            y_pred = y_pred[:, np.newaxis]
        return y_pred

    def score(self, X, y):
        r"""
        Give data, and it returns the coefficient of determination.

        Parameters
        ----------
        X : array-like, shape(n_samples, p_features)
            Sample matrix.
        y : array-like, shape(n_samples, M_responses)
            Real responses for given X.

        Returns
        -------
        score : float
            :math:`R^2` score.
        """
        X, y = new_data_check(self, X, y)

        y_pred = self.predict(X)
        # return -((y - y_pred) * (y - y_pred)).sum()
        return r2_score(y, y_pred)


@ fix_docs
class MultinomialRegression(bess_base):
    r"""
    Adaptive Best-Subset Selection(ABESS) algorithm for
    multiclassification problem.

    Parameters
    ----------
    splicing_type: {0, 1}, optional, default=0
        The type of splicing:
        "0" for decreasing by half, "1" for decresing by one.
    important_search : int, optional, default=128
        The size of inactive set during updating active set when splicing.
        It should be a non-positive integer and if important_search=0,
        it would be set as the size of whole inactive set.

    Examples
    --------
    >>> ### Sparsity known
    >>>
    >>> from abess.linear import MultinomialRegression
    >>> from abess.datasets import make_multivariate_glm_data
    >>> import numpy as np
    >>> np.random.seed(12345)
    >>> data = make_multivariate_glm_data(
    >>>     n = 100, p = 50, k = 10, M = 3, family = 'multinomial')
    >>> model = MultinomialRegression(support_size = 10)
    >>> model.fit(data.x, data.y)
    MultinomialRegression(always_select=[], support_size=10)
    >>> model.predict(data.x)[0:10, ]
    array([1, 0, 0, 0, 1, 1, 1, 2, 1, 2])


    >>> ### Sparsity unknown
    >>>
    >>> # path_type="seq"
    >>> model = MultinomialRegression(path_type = "seq")
    >>> model.fit(data.x, data.y)
    MultinomialRegression(always_select=[])
    >>> model.predict(data.x)[0:10, ]
    array([1, 2, 0, 0, 1, 1, 1, 2, 1, 2])

    >>>
    >>> # path_type="gs"
    >>> model = MultinomialRegression(path_type="gs")
    >>> model.fit(data.x, data.y)
    MultinomialRegression(always_select=[], path_type='gs')
    >>> model.predict(data.x)[0:10, ]
    array([1, 2, 0, 0, 1, 1, 1, 2, 1, 2])

    """

    def __init__(self, max_iter=20, exchange_num=5, path_type="seq",
                 is_warm_start=True, support_size=None,
                 alpha=None, s_min=None, s_max=None,
                 ic_type="ebic", ic_coef=1.0, cv=1,
                 screening_size=-1,
                 always_select=None,
                 primary_model_fit_max_iter=10,
                 primary_model_fit_epsilon=1e-8,
                 #  approximate_Newton=False,
                 thread=1,
                 sparse_matrix=False,
                 splicing_type=0,
                 important_search=128
                 ):
        super().__init__(
            algorithm_type="abess", model_type="Multinomial", normalize_type=2,
            path_type=path_type, max_iter=max_iter, exchange_num=exchange_num,
            is_warm_start=is_warm_start, support_size=support_size,
            alpha=alpha, s_min=s_min, s_max=s_max,
            ic_type=ic_type, ic_coef=ic_coef, cv=cv,
            screening_size=screening_size,
            always_select=always_select,
            primary_model_fit_max_iter=primary_model_fit_max_iter,
            primary_model_fit_epsilon=primary_model_fit_epsilon,
            approximate_Newton=True,
            thread=thread,
            sparse_matrix=sparse_matrix,
            splicing_type=splicing_type,
            important_search=important_search,
            _estimator_type='classifier'
        )

    def _more_tags(self):
        return {'multilabel': False,
                # 'multioutput_only': True,
                'no_validation': True,
                'poor_score': True}

    def predict_proba(self, X):
        r"""
        Give the probabilities of new data being assigned to different classes.

        Parameters
        ----------
        X : array-like, shape(n_samples, p_features)
            Sample matrix to be predicted.

        Returns
        -------
        proba : array-like, shape(n_samples, M_responses)
            Returns the probability of given samples for each class.
            Each column indicates one class.
        """
        X = new_data_check(self, X)

        intercept_ = np.repeat(
            self.intercept_[np.newaxis, ...], X.shape[0], axis=0)
        xbeta = X.dot(self.coef_) + intercept_
        eta = np.exp(xbeta)
        pr = np.zeros_like(xbeta)
        for i in range(X.shape[0]):
            pr[i, :] = eta[i, :] / np.sum(eta[i, :])
        return pr

    def predict(self, X):
        r"""
        Return the most possible class for given data.

        Parameters
        ----------
        X : array-like, shape(n_samples, p_features)
            Sample matrix to be predicted.

        Returns
        -------
        y : array-like, shape(n_samples, M_responses)
            Predict class labels for samples in X.
            Each row contains only one "1", and its column index is the
            predicted class for related sample.
        """
        X = new_data_check(self, X)

        intercept_ = np.repeat(
            self.intercept_[np.newaxis, ...], X.shape[0], axis=0)
        xbeta = X.dot(self.coef_) + intercept_
        max_item = np.argmax(xbeta, axis=1)
        # y_pred = np.zeros_like(xbeta)
        # for i in range(X.shape[0]):
        #     y_pred[i, max_item[i]] = 1
        cl = getattr(self, "classes_", np.arange(self.coef_.shape[1]))
        return cl[max_item]

    def score(self, X, y):
        """
        Give new data, and it returns the prediction accuracy.

        Parameters
        ----------
        X : array-like, shape(n_samples, p_features)
            Test data.
        y : array-like, shape(n_samples, M_responses)
            Test response (dummy variables of real class).

        Returns
        -------
        score : float
            the mean prediction accuracy.
        """
        X, y = new_data_check(self, X, y)
        # if (len(y.shape) == 1 or y.shape[1] == 1):
        #     y, _ = categorical_to_dummy(y.squeeze())

        # pr = self.predict_proba(X)
        # return np.sum(y * np.log(pr))
        y_real = np.zeros(X.shape[0])
        if (len(y.shape) > 1 and y.shape[1] == self.coef_.shape[1]):
            # if given dummy y
            y_real = np.nonzero(y)[1]
        else:
            y_real = y
        y_pred = self.predict(X)
        return (y_real == y_pred).mean()


@ fix_docs
class GammaRegression(bess_base):
    r"""
    Adaptive Best-Subset Selection(ABESS) algorithm for Gamma regression.

    Parameters
    ----------
    splicing_type: {0, 1}, optional, default=0
        The type of splicing:
        "0" for decreasing by half, "1" for decresing by one.
    important_search : int, optional, default=128
        The size of inactive set during updating active set when splicing.
        It should be a non-positive integer and if important_search=0,
        it would be set as the size of whole inactive set.

    Examples
    --------
    >>> ### Sparsity known
    >>>
    >>> from abess.linear import GammaRegression
    >>> from abess.datasets import make_glm_data
    >>> import numpy as np
    >>> np.random.seed(12345)
    >>> data = make_glm_data(n = 100, p = 50, k = 10, family = 'gamma')
    >>> model = GammaRegression(support_size = 10)
    >>> model.fit(data.x, data.y)
    GammaRegression(always_select=[], support_size=10)
    >>> model.predict(data.x)[1:4]
    array([1.34510045e+22, 2.34908508e+30, 1.91570199e+21, 1.29563315e+25])

    >>> ### Sparsity unknown
    >>>
    >>> # path_type="seq"
    >>> model = GammaRegression(path_type = "seq")
    >>> model.fit(data.x, data.y)
    GammaRegression(always_select=[])
    >>> model.predict(data.x)[1:4]
    array([7.03065424e+19, 7.03065424e+19, 7.03065424e+19, 7.03065424e+19])
    >>>
    >>> # path_type="gs"
    >>> model = GammaRegression(path_type="gs")
    >>> model.fit(data.x, data.y)
    GammaRegression(always_select=[], path_type='gs')
    >>> model.predict(data.x)[1:4]
    array([7.03065424e+19, 7.03065424e+19, 7.03065424e+19, 7.03065424e+19])
    """

    def __init__(self, max_iter=20, exchange_num=5, path_type="seq",
                 is_warm_start=True, support_size=None, alpha=None,
                 s_min=None, s_max=None,
                 ic_type="ebic", ic_coef=1.0, cv=1, screening_size=-1,
                 always_select=None,
                 primary_model_fit_max_iter=10, primary_model_fit_epsilon=1e-8,
                 thread=1,
                 sparse_matrix=False,
                 splicing_type=0,
                 important_search=128
                 ):
        super().__init__(
            algorithm_type="abess", model_type="Gamma", normalize_type=2,
            path_type=path_type, max_iter=max_iter, exchange_num=exchange_num,
            is_warm_start=is_warm_start, support_size=support_size,
            alpha=alpha, s_min=s_min, s_max=s_max,
            ic_type=ic_type, ic_coef=ic_coef, cv=cv,
            screening_size=screening_size,
            always_select=always_select,
            primary_model_fit_max_iter=primary_model_fit_max_iter,
            primary_model_fit_epsilon=primary_model_fit_epsilon,
            thread=thread,
            sparse_matrix=sparse_matrix,
            splicing_type=splicing_type,
            important_search=important_search,
            _estimator_type='regressor'
        )

    def _more_tags(self):
        return {'poor_score': True}

    def predict(self, X):
        r"""
        Predict on given data.

        Parameters
        ----------
        X : array-like, shape(n_samples, p_features)
            Sample matrix to be predicted.

        Returns
        -------
        y : array-like, shape(n_samples,)
            Prediction of the mean on given X.
        """
        X = new_data_check(self, X)

        intercept_ = np.ones(X.shape[0]) * self.intercept_
        xbeta_exp = np.exp(X.dot(self.coef_) + intercept_)
        return xbeta_exp

    def score(self, X, y, weights=None):
        r"""
        Give new data, and it returns the prediction error.

        Parameters
        ----------
        X : array-like, shape(n_samples, p_features)
            Sample matrix.
        y : array-like, shape(n_samples, p_features)
            Real response for given X.

        Returns
        -------
        score : float
            Prediction error.
        """
        if weights is None:
            X = np.array(X)
            weights = np.ones(X.shape[0])
        X, y, weights = new_data_check(self, X, y, weights)

        def deviance(y, y_pred):
            dev = 2 * (np.log(y_pred / y) + y / y_pred - 1)
            return np.sum(weights * dev)

        y_pred = self.predict(X)
        y_mean = np.average(y, weights=weights)
        dev = deviance(y, y_pred)
        dev_null = deviance(y, y_mean)
        return 1 - dev / dev_null


@ fix_docs
class OrdinalRegression(bess_base):
    r"""
    Adaptive Best-Subset Selection(ABESS) algorithm for
    ordinal regression problem.

    Parameters
    ----------
    splicing_type: {0, 1}, optional, default=0
        The type of splicing:
        "0" for decreasing by half, "1" for decresing by one.
    important_search : int, optional, default=128
        The size of inactive set during updating active set when splicing.
        It should be a non-positive integer and if important_search=0,
        it would be set as the size of whole inactive set.

    Examples
    --------
    >>> ### Sparsity known
    >>>
    >>> from abess.linear import OrdinalRegression
    >>> from abess.datasets import make_glm_data
    >>> import numpy as np
    >>> np.random.seed(12345)
    >>> data = make_glm_data(n = 1000, p = 50, k = 10, family = 'ordinal')
    >>> print((np.nonzero(data.coef_)[0]))
    [ 0  4 10 14 26 29 34 38 47 48]
    >>> model = OrdinalRegression(support_size = 10)
    >>> model.fit(data.x, data.y)
    classes: [0. 1. 2.]
    OrdinalRegression(support_size=10)
    >>> print((np.nonzero(model.coef_)[0]))
    [ 0  4 10 14 26 29 38 40 47 48]

    >>> ### Sparsity unknown
    >>>
    >>> # path_type="seq"
    >>> model = OrdinalRegression(path_type = "seq")
    >>> model.fit(data.x, data.y)
    classes: [0. 1. 2.]
    OrdinalRegression()
    >>> print((np.nonzero(model.coef_)[0]))
    [ 0  4  8 10 14 26 29 38 40 47 48]
    >>>
    >>> # path_type="gs"
    >>> model = OrdinalRegression(path_type="gs")
    >>> model.fit(data.x, data.y)
    classes: [0. 1. 2.]
    OrdinalRegression(path_type='gs')
    >>> print((np.nonzero(model.coef_)[0]))
    [ 0  4 10 14 26 29 38 47 48]
    """

    def __init__(self, max_iter=20, exchange_num=5, path_type="seq",
                 is_warm_start=True, support_size=None,
                 alpha=None, s_min=None, s_max=None,
                 ic_type="ebic", ic_coef=1.0, cv=1,
                 screening_size=-1,
                 always_select=None,
                 primary_model_fit_max_iter=10,
                 primary_model_fit_epsilon=1e-8,
                 approximate_Newton=False,
                 thread=1,
                 sparse_matrix=False,
                 splicing_type=0,
                 important_search=128
                 ):
        super().__init__(
            algorithm_type="abess", model_type="Ordinal", normalize_type=2,
            path_type=path_type, max_iter=max_iter, exchange_num=exchange_num,
            is_warm_start=is_warm_start, support_size=support_size,
            alpha=alpha, s_min=s_min, s_max=s_max,
            ic_type=ic_type, ic_coef=ic_coef, cv=cv,
            screening_size=screening_size,
            always_select=always_select,
            primary_model_fit_max_iter=primary_model_fit_max_iter,
            primary_model_fit_epsilon=primary_model_fit_epsilon,
            approximate_Newton=approximate_Newton,
            thread=thread,
            sparse_matrix=sparse_matrix,
            splicing_type=splicing_type,
            important_search=important_search,
            # _estimator_type="regressor"
        )

    def predict_proba(self, X):
        r"""
        Give the probabilities of new sample
        being assigned to different classes.

        Parameters
        ----------
        X : array-like, shape(n_samples, p_features)
            Sample matrix to be predicted.

        Returns
        -------
        proba : array-like, shape(n_samples, M_classes)
            Returns the probabilities for each class
            on given X.
        """
        X = new_data_check(self, X)
        M = len(self.intercept_)
        cdf = (X @ self.coef_)[:, np.newaxis] + self.intercept_
        cdf = 1 / (1 + np.exp(-cdf))
        proba = np.zeros_like(cdf)
        proba[:, 0] = cdf[:, 0]
        proba[:, 1:(M - 1)] = cdf[:, 1:(M - 1)] - cdf[:, 0:(M - 2)]
        proba[:, M - 1] = 1 - cdf[:, M - 1]
        return proba

    def predict(self, X):
        r"""
        Return the most possible class label (start from 0) for given data.

        Parameters
        ----------
        X : array-like, shape(n_samples, p_features)
            Sample matrix to be predicted.

        Returns
        -------
        y : array-like, shape(n_samples,)
            Predict class labels for samples in X.
        """
        proba = self.predict_proba(X)
        return np.argmax(proba, axis=1)

    # def score(self, X, y):
    #     """
    #     Give new data, and it returns the entropy function.

    #     Parameters
    #     ----------
    #     X : array-like, shape(n_samples, p_features)
    #         Test data.
    #     y : array-like, shape(n_samples, M_responses)
    #         Test response (dummy variables of real class).

    #     Returns
    #     -------
    #     score : float
    #         entropy function
    #     """
    #     X, y = new_data_check(self, X, y)
    #     if len(y.shape) == 1:
    #         y = categorical_to_dummy(y)

    #     return ???
    
    def score(self, X, y, k=None, sample_weight=None, ignore_ties=False):
        """
        Give new data, and it returns normalized discounted cumulative gain.

        Parameters
        ----------
        X : array-like, shape(n_samples, p_features)
            Test data.
        y : array-like, shape(n_samples, )
            Test response (class labels for samples in X).
        k : int, default=None
            Only consider the highest k scores in the ranking. If None, use all outputs.
        sample_weight : ndarray of shape (n_samples, ), default=None
            If None, all samples are given the same weight.
        ignore_ties : bool, default=False
            Assume that there are no ties in y_pred (which is likely to be the case if y_score is continuous) for efficiency gains.

        Returns
        -------
        score : float
             normalized discounted cumulative gain
        """
        X, y = new_data_check(self, X, y)
        y_pred = self.predict(X)
        ndcg = ndcg_score(y_true=y.reshape(1, -1), y_score=y_pred.reshape(1, -1), k=k, sample_weight=sample_weight, ignore_ties=ignore_ties)
        return ndcg


class abessLogistic(LogisticRegression):
    warning_msg = ("Class ``abessLogistic`` has been renamed to "
                   "``LogisticRegression``. "
                   "The former will be deprecated in version 0.6.0.")
    __doc__ = warning_msg + '\n' + LogisticRegression.__doc__

    def __init__(self, max_iter=20, exchange_num=5, path_type="seq",
                 is_warm_start=True, support_size=None, alpha=None,
                 s_min=None, s_max=None,
                 ic_type="ebic", ic_coef=1.0, cv=1, screening_size=-1,
                 always_select=None,
                 primary_model_fit_max_iter=10, primary_model_fit_epsilon=1e-8,
                 approximate_Newton=False,
                 thread=1,
                 sparse_matrix=False,
                 splicing_type=0,
                 important_search=128,
                 ):
        warnings.warn(self.warning_msg, FutureWarning)
        super().__init__(
            path_type=path_type, max_iter=max_iter, exchange_num=exchange_num,
            is_warm_start=is_warm_start, support_size=support_size,
            alpha=alpha, s_min=s_min, s_max=s_max,
            ic_type=ic_type, ic_coef=ic_coef, cv=cv,
            screening_size=screening_size,
            always_select=always_select,
            primary_model_fit_max_iter=primary_model_fit_max_iter,
            primary_model_fit_epsilon=primary_model_fit_epsilon,
            approximate_Newton=approximate_Newton,
            thread=thread,
            sparse_matrix=sparse_matrix,
            splicing_type=splicing_type,
            important_search=important_search
        )


class abessLm(LinearRegression):
    warning_msg = ("Class ``abessLm`` has been renamed to"
                   " ``LinearRegression``. "
                   "The former will be deprecated in version 0.6.0.")
    __doc__ = warning_msg + '\n' + LinearRegression.__doc__

    def __init__(self, max_iter=20, exchange_num=5, path_type="seq",
                 is_warm_start=True, support_size=None, alpha=None,
                 s_min=None, s_max=None,
                 ic_type="ebic", ic_coef=1.0, cv=1, screening_size=-1,
                 always_select=None,
                 thread=1, covariance_update=False,
                 sparse_matrix=False,
                 splicing_type=0,
                 important_search=128,
                 # primary_model_fit_max_iter=10,
                 # primary_model_fit_epsilon=1e-8, approximate_Newton=False
                 ):
        warnings.warn(self.warning_msg, FutureWarning)
        super().__init__(
            path_type=path_type, max_iter=max_iter, exchange_num=exchange_num,
            is_warm_start=is_warm_start, support_size=support_size,
            alpha=alpha, s_min=s_min, s_max=s_max,
            ic_type=ic_type, ic_coef=ic_coef, cv=cv,
            screening_size=screening_size,
            always_select=always_select,
            thread=thread, covariance_update=covariance_update,
            sparse_matrix=sparse_matrix,
            splicing_type=splicing_type,
            important_search=important_search
        )


class abessCox(CoxPHSurvivalAnalysis):
    warning_msg = ("Class ``abessCox`` has been renamed to "
                   "``CoxPHSurvivalAnalysis``. "
                   "The former will be deprecated in version 0.6.0.")
    __doc__ = warning_msg + '\n' + CoxPHSurvivalAnalysis.__doc__

    def __init__(self, max_iter=20, exchange_num=5, path_type="seq",
                 is_warm_start=True, support_size=None, alpha=None,
                 s_min=None, s_max=None,
                 ic_type="ebic", ic_coef=1.0, cv=1, screening_size=-1,
                 always_select=None,
                 primary_model_fit_max_iter=10, primary_model_fit_epsilon=1e-8,
                 approximate_Newton=False,
                 thread=1,
                 sparse_matrix=False,
                 splicing_type=0,
                 important_search=128
                 ):
        warnings.warn(self.warning_msg, FutureWarning)
        super().__init__(
            path_type=path_type, max_iter=max_iter, exchange_num=exchange_num,
            is_warm_start=is_warm_start, support_size=support_size,
            alpha=alpha, s_min=s_min, s_max=s_max,
            ic_type=ic_type, ic_coef=ic_coef, cv=cv,
            screening_size=screening_size,
            always_select=always_select,
            primary_model_fit_max_iter=primary_model_fit_max_iter,
            primary_model_fit_epsilon=primary_model_fit_epsilon,
            approximate_Newton=approximate_Newton,
            thread=thread,
            sparse_matrix=sparse_matrix,
            splicing_type=splicing_type,
            important_search=important_search
        )


class abessPoisson(PoissonRegression):
    warning_msg = ("Class ``abessPoisson`` has been renamed to "
                   "``PoissonRegression``. "
                   "The former will be deprecated in version 0.6.0.")
    __doc__ = warning_msg + '\n' + PoissonRegression.__doc__

    def __init__(self, max_iter=20, exchange_num=5, path_type="seq",
                 is_warm_start=True, support_size=None, alpha=None,
                 s_min=None, s_max=None,
                 ic_type="ebic", ic_coef=1.0, cv=1, screening_size=-1,
                 always_select=None,
                 primary_model_fit_max_iter=10, primary_model_fit_epsilon=1e-8,
                 thread=1,
                 sparse_matrix=False,
                 splicing_type=0,
                 important_search=128
                 ):
        warnings.warn(self.warning_msg, FutureWarning)
        super().__init__(
            path_type=path_type, max_iter=max_iter, exchange_num=exchange_num,
            is_warm_start=is_warm_start, support_size=support_size,
            alpha=alpha, s_min=s_min, s_max=s_max,
            ic_type=ic_type, ic_coef=ic_coef, cv=cv,
            screening_size=screening_size,
            always_select=always_select,
            primary_model_fit_max_iter=primary_model_fit_max_iter,
            primary_model_fit_epsilon=primary_model_fit_epsilon,
            thread=thread,
            sparse_matrix=sparse_matrix,
            splicing_type=splicing_type,
            important_search=important_search
        )


class abessMultigaussian(MultiTaskRegression):
    warning_msg = ("Class ``abessMultigaussian`` has been renamed to "
                   "``MultiTaskRegression``. "
                   "The former will be deprecated in version 0.6.0.")
    __doc__ = warning_msg + '\n' + MultiTaskRegression.__doc__

    def __init__(self, max_iter=20, exchange_num=5, path_type="seq",
                 is_warm_start=True, support_size=None, alpha=None,
                 s_min=None, s_max=None,
                 ic_type="ebic", ic_coef=1.0, cv=1, screening_size=-1,
                 always_select=None,
                 thread=1, covariance_update=False,
                 sparse_matrix=False,
                 splicing_type=0,
                 important_search=128
                 ):
        warnings.warn(self.warning_msg, FutureWarning)
        super().__init__(
            path_type=path_type, max_iter=max_iter, exchange_num=exchange_num,
            is_warm_start=is_warm_start, support_size=support_size,
            alpha=alpha, s_min=s_min, s_max=s_max,
            ic_type=ic_type, ic_coef=ic_coef, cv=cv,
            screening_size=screening_size,
            always_select=always_select,
            thread=thread, covariance_update=covariance_update,
            sparse_matrix=sparse_matrix,
            splicing_type=splicing_type,
            important_search=important_search
        )


class abessMultinomial(MultinomialRegression):
    warning_msg = ("Class ``abessMultinomial`` has been renamed to "
                   "``MultinomialRegression``. "
                   "The former will be deprecated in version 0.6.0.")
    __doc__ = warning_msg + '\n' + MultinomialRegression.__doc__

    def __init__(self, max_iter=20, exchange_num=5, path_type="seq",
                 is_warm_start=True, support_size=None,
                 alpha=None, s_min=None, s_max=None,
                 ic_type="ebic", ic_coef=1.0, cv=1, screening_size=-1,
                 always_select=None,
                 primary_model_fit_max_iter=10, primary_model_fit_epsilon=1e-8,
                 # approximate_Newton=False,
                 thread=1,
                 sparse_matrix=False,
                 splicing_type=0,
                 important_search=128
                 ):
        warnings.warn(self.warning_msg, FutureWarning)
        super().__init__(
            path_type=path_type, max_iter=max_iter, exchange_num=exchange_num,
            is_warm_start=is_warm_start, support_size=support_size,
            alpha=alpha, s_min=s_min, s_max=s_max,
            ic_type=ic_type, ic_coef=ic_coef, cv=cv,
            screening_size=screening_size,
            always_select=always_select,
            primary_model_fit_max_iter=primary_model_fit_max_iter,
            primary_model_fit_epsilon=primary_model_fit_epsilon,
            # approximate_Newton=approximate_Newton,
            thread=thread,
            sparse_matrix=sparse_matrix,
            splicing_type=splicing_type,
            important_search=important_search
        )


class abessGamma(GammaRegression):
    warning_msg = ("Class ``abessGamma`` has been renamed to "
                   "``GammaRegression``. "
                   "The former will be deprecated in version 0.6.0.")
    __doc__ = warning_msg + '\n' + GammaRegression.__doc__

    def __init__(self, max_iter=20, exchange_num=5, path_type="seq",
                 is_warm_start=True, support_size=None, alpha=None,
                 s_min=None, s_max=None,
                 ic_type="ebic", ic_coef=1.0, cv=1, screening_size=-1,
                 always_select=None,
                 primary_model_fit_max_iter=10,
                 primary_model_fit_epsilon=1e-8,
                 thread=1,
                 sparse_matrix=False,
                 splicing_type=0,
                 important_search=128
                 ):
        warnings.warn(self.warning_msg, FutureWarning)
        super().__init__(
            path_type=path_type, max_iter=max_iter, exchange_num=exchange_num,
            is_warm_start=is_warm_start, support_size=support_size,
            alpha=alpha, s_min=s_min, s_max=s_max,
            ic_type=ic_type, ic_coef=ic_coef, cv=cv,
            screening_size=screening_size,
            always_select=always_select,
            primary_model_fit_max_iter=primary_model_fit_max_iter,
            primary_model_fit_epsilon=primary_model_fit_epsilon,
            thread=thread,
            sparse_matrix=sparse_matrix,
            splicing_type=splicing_type,
            important_search=important_search
        )
