# EDA
# -------------------------------
from pandas_profiling import ProfileReport



# data cleaning
# -------------------------------
# pyjanitor
# https://github.com/ericmjl/pyjanitor



# baseline model
# -------------------------------
from sklearn.dummy import DummyRegressor
from sklearn.metrics import make_scorer
scorer = make_scorer(mean_squared_error)
scores_dummy = cross_val_score(baseline, train_df.values, y, cv=RepeatedKFold(n_repeats=100), scoring=scorer)



# feature importance
# ------------------------------
from eli5.sklearn import PermutationImportance




# feature engineering and encoding
# -----------------------------
# Category Encoding
# http://contrib.scikit-learn.org/categorical-encoding/index.html

import category_encoders as ce
encoder = ce.LeaveOneOutEncoder(cols=[...])
encoder.fit(X, y)
X_cleaned = encoder.transform(X_dirty)




# imputing
# ------------------------------
from fancyimpute import KNN
X_filled_knn = KNN(k=3).fit_transform(X_incomplete)



# imbalanced data
# ------------------------------
# https://imbalanced-learn.org/en/stable/index.html



# scaling and outlier handling
# -----------------------------



# stacking
# -----------------------------
# https://github.com/vecxoz/vecstack



# HPO
# -----------------------------




# blending
# ---------------------------
