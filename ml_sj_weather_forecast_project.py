# -*- coding: utf-8 -*-
"""ML SJ Weather Forecast Project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1lGbWss0Agak3MfYymNIGgm8NojodTy20

# **Weather Forecast - Temperature for San Jose (using historical data)**
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from numpy import linalg as LA
import tensorflow as tf
from sklearn.metrics import explained_variance_score, mean_absolute_error, median_absolute_error
from sklearn.model_selection import train_test_split
import seaborn as sns
sns.set_theme()

weather = pd.read_csv("San Jose Weather Data.csv", index_col="DATE")
data = weather.values
print(weather.head())

"""**Data Preprocessing/Cleaning**"""

print("%age of null values in each column")
weather.apply(pd.isnull).sum()*100/weather.shape[0]

explodes = (0,0.3)
plt.pie(weather.TMAX.isna().value_counts(),explode=explodes,startangle=0,
   labels=['Non NaN elements','NaN elements'], textprops={'fontsize': 20})

explodes = (0,0.3)
plt.pie(weather.AWND.isna().value_counts(),explode=explodes,startangle=0,
   labels=['Non NaN elements','NaN elements'], textprops={'fontsize': 20})

core_weather = weather[["AWND","PRCP","TMAX","TMIN"]].copy()
core_weather

core_weather.columns = ["windspeed","precip","tempmax","tempmin"]
core_weather

print("%age of null values in each column of core weather features")
core_weather.apply(pd.isnull).sum()*100/core_weather.shape[0]

core_weather[pd.isnull(core_weather["windspeed"])]

core_weather["windspeed"] = core_weather["windspeed"].fillna(0)
core_weather.apply(pd.isnull).sum()

core_weather[pd.isnull(core_weather["tempmax"])]

core_weather = core_weather.fillna(method="ffill")
core_weather.apply(pd.isnull).sum()

core_weather.index

core_weather.index = pd.to_datetime(core_weather.index)
core_weather.index

corrmatrix = core_weather.corr()
sns.heatmap(corrmatrix, annot = True, cmap= 'YlGnBu')

core_weather[["tempmax", "tempmin"]].plot()

core_weather["precip"].plot()

core_weather.groupby(core_weather.index.year).apply(lambda x: x["precip"].sum()).plot()

"""# **We plan to predict the weather (maximum Temperature) for the next day, based on the historical data.**"""

core_weather["target"] = core_weather.shift(-1)["tempmax"]

core_weather = core_weather.iloc[:-1,:].copy()

core_weather

core_weather.hist(bins = 40, figsize = (15,10))
plt.show()

from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge
#reg = LinearRegression()
reg = Ridge(alpha=.1)

predictors = ["windspeed","precip","tempmax","tempmin"]

plt.plot(core_weather["tempmax"],core_weather["target"],'go')
plt.xlabel("tempmax")
plt.ylabel("target")
plt.show()

plt.plot(core_weather["precip"],core_weather["target"],'go')
plt.xlabel("precipitation")
plt.ylabel("target")
plt.show()

plt.plot(core_weather["windspeed"],core_weather["target"],'go')
plt.xlabel("windspeed")
plt.ylabel("target")
plt.show()

train = core_weather.loc[:"2020-12-31"]
test = core_weather.loc["2021-01-01":]

train

test

reg.fit(train[predictors], train["target"])

predictions = reg.predict(test[predictors])

from sklearn.metrics import mean_squared_error

mean_squared_error(test["target"], predictions)

combined = pd.concat([test["target"], pd.Series(predictions, index=test.index)], axis=1)
combined.columns = ["actual", "predictions"]
combined

combined.plot()

reg.coef_

core_weather["month_max"] = core_weather["tempmax"].rolling(30).mean()

core_weather["month_day_max"] = core_weather["month_max"] / core_weather["tempmax"]

core_weather["max_min"] = core_weather["tempmax"] / core_weather["tempmin"]

core_weather = core_weather.iloc[30:,:].copy()

def create_predictions(predictors, core_weather, reg):
    train = core_weather.loc[:"2020-12-31"]
    test = core_weather.loc["2021-01-01":]

    reg.fit(train[predictors], train["target"])
    predictions = reg.predict(test[predictors])

    error = mean_squared_error(test["target"], predictions)
    
    combined = pd.concat([test["target"], pd.Series(predictions, index=test.index)], axis=1)
    combined.columns = ["actual", "predictions"]
    return error, combined

predictors = ["windspeed","precip","tempmax","tempmin","month_max","month_day_max", "max_min"]

error, combined = create_predictions(predictors, core_weather, reg)
error

combined.plot()

core_weather["monthly_avg"] = core_weather["tempmax"].groupby(core_weather.index.month).apply(lambda x: x.expanding(1).mean())
core_weather["day_of_year_avg"] = core_weather["tempmax"].groupby(core_weather.index.day_of_year).apply(lambda x: x.expanding(1).mean())
core_weather

core_weather["monthly_avg"].plot()

error, combined = create_predictions(predictors + ["monthly_avg", "day_of_year_avg"], core_weather, reg)
error

combined.plot()

core_weather.corr()["target"]

"""Correlation Heat Map - How correlated are the predictors with each other and also the target variable"""

corrmatrix = core_weather.corr()
sns.heatmap(corrmatrix, annot = True, cmap= 'YlGnBu')

combined["diff"] = (combined["actual"] - combined["predictions"]).abs()

combined.sort_values("diff", ascending=False).head(10)

w = reg.coef_
w

core_weather.corr()["target"]

combined.sort_values("diff", ascending=False).head()

from sklearn.metrics import explained_variance_score, mean_absolute_error, median_absolute_error
from sklearn.model_selection import train_test_split

core_weather = core_weather.reset_index(drop=True)

X = core_weather[[col for col in core_weather.columns if col != 'target']]

y = core_weather["target"]

X_train, X_tmp, y_train, y_tmp = train_test_split(X, y, test_size=0.2, random_state=23)

X_test, X_val, y_test, y_val = train_test_split(X_tmp, y_tmp, test_size=0.5, random_state=23)

X_train.shape, X_test.shape, X_val.shape
print("Training instances   {}, Training features   {}".format(X_train.shape[0], X_train.shape[1]))
print("Validation instances {}, Validation features {}".format(X_val.shape[0], X_val.shape[1]))
print("Testing instances    {}, Testing features    {}".format(X_test.shape[0], X_test.shape[1]))

plt.plot(X, y, 'go')
plt.xlabel("Core_weather predictors")
plt.ylabel("Target Temp")
plt.show()

### Plot the fitted curve

yhat = np.dot(np.sort(X, axis=0),w)

plt.plot(X, y, 'go')
plt.plot(X, yhat, 'b', label="Linear Regression")
plt.legend()
plt.xlabel("Core_weather predictors")
plt.ylabel("Target temp")
plt.show()

yhat

core_weather

"""# **Using DNN Regressor (Deep Neural Network) for predicting temperature for the next day**"""

feature_cols = [tf.feature_column.numeric_column(col) for col in X.columns]

"""Using DNN Regressor Model from the Tensor Flow Estimator library"""

regressor = tf.estimator.DNNRegressor(feature_columns=feature_cols,
                                      hidden_units=[50, 50],
                                      model_dir='tf_wx_model')

def wx_input_fn(X, y=None, num_epochs=None, shuffle=True, batch_size=400):
    return tf.compat.v1.estimator.inputs.pandas_input_fn(x=X,
                                               y=y,
                                               num_epochs=num_epochs,
                                               shuffle=shuffle,
                                               batch_size=batch_size)

"""# **Running the Training regressor 100 times, with batch size of 400 instances each time**"""

evaluations = []
STEPS = 400
for i in range(100):
  regressor.train(input_fn=wx_input_fn(X_train, y=y_train), steps=STEPS)
  evaluations.append(regressor.evaluate(input_fn=wx_input_fn(X_val, y_val, num_epochs=1, shuffle=False)))

evaluations[0]

# Commented out IPython magic to ensure Python compatibility.
import matplotlib.pyplot as plt
# %matplotlib inline

# manually set the parameters of the figure to and appropriate size
plt.rcParams['figure.figsize'] = [14, 10]

loss_values = [ev['loss'] for ev in evaluations]
training_steps = [ev['global_step'] for ev in evaluations]

plt.scatter(x=training_steps, y=loss_values)
plt.xlabel('Training steps')
plt.ylabel('Loss (SSE)')
plt.show()

pred = regressor.predict(input_fn=wx_input_fn(X_test, num_epochs=1, shuffle=False))
predictions = np.array([p['predictions'][0] for p in pred])

print("\nThe Explained Variance: %.2f" % explained_variance_score(y_test, predictions))  
print("The Mean Absolute Error: %.2f degrees Fahrenheit" % mean_absolute_error(y_test, predictions))  
print("The Median Absolute Error: %.2f degrees Fahrenheit" % median_absolute_error(y_test, predictions))

print(predictions[:10])

pred_xtest_lastvalue = regressor.predict(input_fn=wx_input_fn(X_test[len(X_test)-1:],
                                              num_epochs=1,
                                              shuffle=False))
predictions1 = np.array([p['predictions'][0] for p in pred_xtest_lastvalue])
print(X_test)
print(y_test)

print("The predicted value for maximum temperature for the next day using the last instance in the test input is {} degree Fahrenheit ".format(predictions1[0]))