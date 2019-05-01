# Machine Learning Plan #
   

## Classes ##

- Introduction to Machine Learning for Coders, fast.ai [DONE]
- Deep Learning, fast.ai [in progress]
- Computational Linear Algebra, fast.ai [TBD]
- [mlcourse.ai](https://mlcourse.ai/) [Schedule to start Sept 9, 2019]

## Reading ##

- Deep Learning Book, [math prerequesites](http://www.deeplearningbook.org/). [TBD]
- Feature Engineering Talk, [slides link](https://www.slideshare.net/HJvanVeen/feature-engineering-72376750). [TBD]

## Lectures ##

- [Owen Zhang](https://www.kaggle.com/owenzhang1) talk at NYC Data Academy ([link](https://www.youtube.com/watch?v=LgLcfZjNF44)). Key ideas on model stacking (using glm on sparse and then feeding into xgb); using leave-one-out target encoding for high cardinality categorical variables; gbm tuning.
- [raddar]() My Journey to Kaggle Grandmasster, Kaggle Days talk [link](https://www.youtube.com/watch?v=7XEMPU17-Wo).
- [CPMP]() Beyond Feature Engineering and HPO, Kaggle Days talk [link](https://www.youtube.com/watch?v=fH_FiquKhiI).
- Vincent W. Winning with Linear Models [link](https://www.youtube.com/watch?v=68ABAU_V8qI).
- Vincent W. The Duct Tape of Heroes (Bayesian stats; pomegranate) [link](https://www.youtube.com/watch?v=dE5j6NW-Kzg).



# Machine Learning Pipeline #

## EDA ##

```python
from pandas_profiling import ProfileReport
```


## Data Cleaning ##

-  `pyjanitor`  https://github.com/ericmjl/pyjanitor



## Baseline Random Model ##

```python
from sklearn.dummy import DummyRegressor
from sklearn.metrics import make_scorer
scorer = make_scorer(mean_squared_error)
scores_dummy = cross_val_score(baseline, train_df.values, y, cv=RepeatedKFold(n_repeats=100), scoring=scorer)
```


## Feature Importance and Explanability ##

```python
from eli5.sklearn import PermutationImportance
```

- `tree_iterpreter`
- `shap`
- Jeremy's dendrogram code to inspect for redundant features
- Jeremy's RF code to see if feature can predict if a sample is in/out of the test set. If it can, this means that 


## Feature Engineering and Encoding ##

-  Category Encoding  http://contrib.scikit-learn.org/categorical-encoding/index.html

```python
import category_encoders as ce
encoder = ce.LeaveOneOutEncoder(cols=[...])
encoder.fit(X, y)
X_cleaned = encoder.transform(X_dirty)
```



## Imputing ##

~~~{.python}
from fancyimpute import KNN
X_filled_knn = KNN(k=3).fit_transform(X_incomplete)
~~~


## Imbalanced Data and Data Augmentation ##
-  https://imbalanced-learn.org/en/stable/index.html



## Scaling and Outlier Handling ##




## Model Stacking ##
- `vectack` package compat with `sklearn` api,  https://github.com/vecxoz/vecstack


## Hyperparameter Optimzation ##
- `BayesOptCV`



## Blending ##


## Using Neptune ##



# Bayesian Learning #

- 
