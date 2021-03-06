# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 16:31:23 2019

@author: michaelboles
"""

# set up working directory
import os
#os.chdir('/Users/michaelboles/Michael/Coding/2019/Realestate') # Mac
os.chdir('C:\\Users\\bolesmi\\Lam\\Coding\\Python\\2019\\Realestate') # PC

# import packages
import pandas as pd
import statsmodels.formula.api as smf

# import full dataset 
data_all_raw = pd.read_csv('./data/listings/data_all.csv')

# format/clean -- select columns of interest, drop rows with zeros, NaNs
data_all_temp2 = data_all_raw.dropna()
data_all_temp3 = data_all_temp2[(data_all_temp2 != 0).all(1)]

# get rid of some outliers
data_all_temp4 = data_all_temp3[data_all_temp3['Home size'] < 5000]
data_all_temp5 = data_all_temp4[data_all_temp4['Lot size'] < 20000]
data_all_temp6 = data_all_temp5[data_all_temp5['Price'] < 5000000]
data_all_temp7 = data_all_temp6[data_all_temp6['Beds'] < 6]
data_all_temp8 = data_all_temp7[data_all_temp7['Baths'] < 6]

# remove spaces in column names - necessary for OLS?
data_all_temp8.columns = data_all_temp8.columns.str.replace(' ', '_')
data_all = data_all_temp8

# check for multicollinearity
correlations = data_all.corr()

# query count, mean, stdev etc. of selected data
data_all.describe()

## option to select one zipcode
#zipcode = 94401
#data_subset = data_all[data_all['Zip'] == zipcode]

### BUILD MODEL ###

# build model from data using backward elimination
formula_1 = 'Price ~ Home_size + Lot_size + Beds + Baths + Commute_time + School_score'
formula_2 = 'Price ~ Home_size + Lot_size + Beds + Commute_time + School_score'
formula_3 = 'Price ~ Home_size + Lot_size + Commute_time + School_score'
formula_4 = 'Price ~ Home_size + Lot_size + Beds + Baths'
regressor = smf.ols(formula_4, data = data_all).fit() # settled on formula_3
regressor.summary()
summary = regressor.summary()
summary_text = summary.as_text()

## try same for only one zipcode
#data_subset = data_all.loc[data_all['Zip'] == 95126]
#formula_subset_1 = 'Price ~ Home_size + Lot_size + Beds + Baths + Commute_time + School_score'
#formula_subset_2 = 'Price ~ Home_size + Lot_size + Baths'
#regressor = smf.ols(formula_subset_2, data = data_subset).fit()
#summary_subset = regressor.summary()
#summary_subset_text = summary_subset.as_text()

# get variance inflation factor
from statsmodels.stats.outliers_influence import variance_inflation_factor
variables = regressor.model.exog
vif = [variance_inflation_factor(variables, i) for i in range(variables.shape[1])]



### sklearn ###

# set features (independent) and labels (dependent)
x = data_all[['Home_size', 'Lot_size', 'Commute_time', 'School_score']]
y = data_all['Price']

# before commute, school quality data
x2 = data_all[['Home_size', 'Lot_size', 'Beds', 'Baths']]

# fit data
from sklearn.linear_model import LinearRegression
regressor = LinearRegression()
regressor.fit(x2, y)
#regressor.intercept_, regressor.coef_

# predict values based on model
y_pred = regressor.predict(x) # listing + surroundings data
y_pred2 = regressor.predict(x2) # listing data only

# calculate difference between predicted and actual prices
diff = round((y - y_pred2), 6)

# add difference to full data set
data_all['Price difference 2'] = diff
#data_all.to_csv('data_all_price_predictions.csv')

# import fitted data
data_all = pd.read_csv('./data/listings/data_all_price_predictions.csv')

# set up histogram text box
description = data_all['Price difference'].describe()
prices_textbox = 'Median = -$%.2f M \nStdev = $%.2f M' % (round(-description['50%']/100000,4), round(description['std']/1000000,4))

# plot price difference
from plotfunctions import plothist2
figure_name = 'price_diff_loc_data.jpg'
binwidth = 100
data1 = data_all['Price difference']/1000000
data2 = data_all['Price difference 2']/1000000
plothist2(data1, data2, 0.1, prices_textbox, -1, 1, 'Actual - predicted price ($M)', 'Counts', figure_name)

# plot price difference in seaborn
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

# Plot histograms
plt.figure(figsize=(5,5))
ax1 = sns.distplot(data1, kde=False, color='blue', hist_kws=dict(edgecolor="k", linewidth=.5))
ax2 = sns.distplot(data2, kde=False, color='orangered', hist_kws=dict(edgecolor="k", linewidth=.5))
plt.xlabel('Actual - predicted price ($M)', fontsize=13) #, fontweight='bold')
plt.ylabel('Counts', fontsize=13) #, fontweight='bold')
#plt.legend()
plt.xticks(np.arange(-1, 1.1, 0.25))
plt.xlim(-1,1)
plt.savefig('.\Images\pricediffhist.jpg', dpi=600)

