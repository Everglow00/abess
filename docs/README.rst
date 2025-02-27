Welcome to ``abess``'s documentation!
==========================================================================

.. raw:: html

   <!-- badges: start -->

   
|logopic|      

.. |logopic| image:: ./image/icon_long.png    


|Python build status| |R build status| |codecov| |docs| |cran| |pypi| |conda-forge| |pyversions| |License| |Codacy|

.. |Codacy| image:: https://app.codacy.com/project/badge/Grade/3f6e60a3a3e44699a033159633981b76 
   :target: https://www.codacy.com/gh/abess-team/abess/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=abess-team/abess&amp;utm_campaign=Badge_Grade
.. |Travis build status| image:: https://travis-ci.com/abess-team/abess.svg?branch=master
   :target: https://travis-ci.com/abess-team/abess
.. |Python build status| image:: https://github.com/abess-team/abess/actions/workflows/python_test.yml/badge.svg?branch=master
   :target: https://github.com/abess-team/abess/actions/workflows/python_test.yml
.. |R build status| image:: https://github.com/abess-team/abess/actions/workflows/r_test.yml/badge.svg?branch=master
   :target: https://github.com/abess-team/abess/actions/workflows/r_test.yml
.. |codecov| image:: https://codecov.io/gh/abess-team/abess/branch/master/graph/badge.svg?token=LK56LHXV00
   :target: https://codecov.io/gh/abess-team/abess
.. |docs| image:: https://readthedocs.org/projects/abess/badge/?version=latest
   :target: https://abess.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
.. |R website| image:: https://github.com/abess-team/abess/actions/workflows/r_website.yml
   :target: https://abess-team.github.io/abess/
.. |cran| image:: https://img.shields.io/cran/v/abess?logo=R
   :target: https://cran.r-project.org/package=abess
.. |pypi| image:: https://badge.fury.io/py/abess.svg
   :target: https://badge.fury.io/py/abess
.. |conda-forge| image:: https://img.shields.io/conda/vn/conda-forge/abess.svg
   :target: https://anaconda.org/conda-forge/abess
.. |pyversions| image:: https://img.shields.io/pypi/pyversions/abess
.. |License| image:: https://img.shields.io/badge/License-GPL%20v3-blue.svg 
   :target: http://www.gnu.org/licenses/gpl-3.0


Overview
============

``abess`` (Adaptive BEst Subset Selection) library aims to solve general best subset selection, i.e., 
find a small subset of predictors such that the resulting model is expected to have the highest accuracy. 
The selection for best subset shows great value in scientific researches and practical applications. 
For example, clinicians want to know whether a patient is healthy or not  
based on the expression level of a few of important genes.

This library implements a generic algorithm framework to find the optimal solution in an extremely fast way [#1abess]_. 
This framework now supports the detection of best subset under: 
`linear regression`_, `(multi-class) classification`_, `censored-response modeling`_ [#4sksurv]_, 
`multi-response modeling (a.k.a. multi-tasks learning)`_, etc. 
It also supports the variants of best subset selection like 
`group best subset selection`_ [#2gbes]_ and `nuisance best subset selection`_ [#3nbes]_. 
Especially, the time complexity of (group) best subset selection for linear regression is certifiably polynomial [#1abess]_ [#2gbes]_.

.. _linear regression: https://abess.readthedocs.io/en/latest/auto_gallery/1-glm/plot_1_LinearRegression.html
.. _(multi-class) classification: https://abess.readthedocs.io/en/latest/auto_gallery/1-glm/plot_2_LogisticRegression.html
.. _counting-response modeling: https://abess.readthedocs.io/en/latest/auto_gallery/1-glm/plot_5_PossionGammaRegression.html
.. _censored-response modeling: https://abess.readthedocs.io/en/latest/auto_gallery/1-glm/plot_4_CoxRegression.html#sphx-glr-auto-gallery-1-glm-plot-4-coxregression-py
.. _multi-response modeling (a.k.a. multi-tasks learning): https://abess.readthedocs.io/en/latest/auto_gallery/1-glm/plot_3_MultiTaskLearning.html
.. _group best subset selection: https://abess.readthedocs.io/en/latest/auto_gallery/3-advanced-features/plot_best_group.html
.. _nuisance best subset selection: https://abess.readthedocs.io/en/latest/auto_gallery/3-advanced-features/plot_best_nuisance.html

Quick start
============

The ``abess`` software has both Python and R's interfaces. Here a quick start will be given and
for more details, please view: `Installation`_.

.. _Installation: https://abess.readthedocs.io/en/latest/Installation.html

Python package
--------------

Install the stable ``abess`` Python package from `PyPI <https://pypi.org/project/abess/>`_: 

.. code-block:: shell

   $ pip install abess
   
or `conda-forge <https://anaconda.org/conda-forge/abess>`_

.. code-block:: shell

   $ conda install abess

Best subset selection for linear regression on a simulated dataset in Python:    

.. code-block:: python

   from abess.linear import abessLm
   from abess.datasets import make_glm_data
   sim_dat = make_glm_data(n = 300, p = 1000, k = 10, family = "gaussian")
   model = abessLm()
   model.fit(sim_dat.x, sim_dat.y)

See more examples analyzed with Python in the `Python tutorials <https://abess.readthedocs.io/en/latest/auto_gallery/index.html>`_.


R package
-----------

Install ``abess`` from `R CRAN <https://cran.r-project.org/web/packages/abess>`_ by running the following command in R: 

.. code-block:: r

   install.packages("abess")


Best subset selection for linear regression on a simulated dataset in R:

.. code-block:: r

   library(abess)
   sim_dat <- generate.data(n = 300, p = 1000)
   abess(x = sim_dat[["x"]], y = sim_dat[["y"]])

See more examples analyzed with R in the `R tutorials <https://abess-team.github.io/abess/articles/>`_.

Runtime Performance
===================

To show the power of ``abess`` in computation, 
we assess its timings of the CPU execution (seconds) on synthetic datasets, and compare them to 
state-of-the-art variable selection methods. 
The variable selection and estimation results as well as the details of settings are deferred to `Python performance`_  
and `R performance`_. All computations are conducted on a Ubuntu platform with Intel(R) Core(TM) i9-9940X CPU @ 3.30GHz and 48 RAM.

.. _Python performance: https://abess.readthedocs.io/en/latest/auto_gallery/1-glm/plot_a1_power_of_abess.html
.. _R performance: https://abess-team.github.io/abess/articles/v11-power-of-abess.html

Python package   
---------------

We compare ``abess`` Python package with scikit-learn on linear regression and logistic regression.
Results are presented in the below figure:
|pic1| 

.. |pic1| image:: ./image/timings.png
   :width: 100%

It can be seen that ``abess`` uses the least runtime to find the solution. The results can be reproduced by running the commands in shell:

.. code-block:: shell

   $ python ./docs/simulation/Python/timings.py


R package    
-----------

We compare ``abess`` R package with three widely used R packages: `glmnet`, `ncvreg`, and `L0Learn`. 
We get the runtime comparison result:

|Rpic1|

.. |Rpic1| image:: ./image/r_runtime.png
   :width: 100%

Compared with the other packages, 
``abess`` shows competitive computational efficiency, and achieves the best computational power when variables have a large correlation.

Conducting the following commands in shell can reproduce the above results: 

.. code-block:: shell

   $ Rscript ./docs/simulation/R/timings.R

Open source software     
====================

``abess`` is a free software and its source code is publicly available in `Github`_.  
The core framework is programmed in C++, and user-friendly R and Python interfaces are offered.
You can redistribute it and/or modify it under the terms of the `GPL-v3 License`_. 
We welcome contributions for ``abess``, especially stretching ``abess`` to 
the other best subset selection problems. 

.. _github: https://github.com/abess-team/abess
.. _GPL-v3 License: https://www.gnu.org/licenses/gpl-3.0.html

What's new
===========

Version 0.4.5:

- `abess` Python package can be installed via `conda`. 
- Easier installation for Python users
- ``abess`` R package is is highlighted as one of the core packages in `CRAN Task View: Machine Learning & Statistical Learning <https://cran.r-project.org/web/views/MachineLearning.html>`__.
- Support predicting survival function in `abess.linear.CoxPHSurvivalAnalysis`.
- Rename estimators in Python. Please check `here <https://abess.readthedocs.io/en/latest/Python-package/index.html>`__.

New best subset selection tasks: 

- Generalized linear model for ordinal regression (a.k.a rank learning in some machine learning literature).

Citation         
==========

If you use ``abess`` or reference our tutorials in a presentation or publication, we would appreciate citations of our library [#5abesslib]_.

| Jin Zhu, Liyuan Hu, Junhao Huang, Kangkang Jiang, Yanhang Zhang, Shiyun Lin, Junxian Zhu, Xueqin Wang (2021). “abess: A Fast Best Subset Selection Library in Python and R.” arXiv:2110.09697.

The corresponding BibteX entry:

.. code-block:: shell

   @article{zhu-abess-arxiv,
      author  = {Jin Zhu and Liyuan Hu and Junhao Huang and Kangkang Jiang and Yanhang Zhang and Shiyun Lin and Junxian Zhu and Xueqin Wang},
      title   = {abess: A Fast Best Subset Selection Library in Python and R},
      journal = {arXiv:2110.09697},
      year    = {2021},
   }

References
==========

.. [#1abess] Junxian Zhu, Canhong Wen, Jin Zhu, Heping Zhang, and Xueqin Wang (2020). A polynomial algorithm for best-subset selection problem. Proceedings of the National Academy of Sciences, 117(52):33117-33123.

.. [#4sksurv] Pölsterl, S (2020). scikit-survival: A Library for Time-to-Event Analysis Built on Top of scikit-learn. J. Mach. Learn. Res., 21(212), 1-6.

.. [#2gbes] Yanhang Zhang, Junxian Zhu, Jin Zhu, and Xueqin Wang (2021). Certifiably Polynomial Algorithm for Best Group Subset Selection. arXiv preprint arXiv:2104.12576.

.. [#3nbes] Qiang Sun and Heping Zhang (2020). Targeted Inference Involving High-Dimensional Data Using Nuisance Penalized Regression, Journal of the American Statistical Association, DOI: 10.1080/01621459.2020.1737079.

.. [#5abesslib] Jin Zhu, Liyuan Hu, Junhao Huang, Kangkang Jiang, Yanhang Zhang, Shiyun Lin, Junxian Zhu, and Xueqin Wang (2021). abess: A Fast Best Subset Selection Library in Python and R. arXiv preprint arXiv:2110.09697.
    
