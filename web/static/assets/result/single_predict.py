from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2

from sklearn.model_selection import KFold
from sklearn.ensemble import GradientBoostingRegressor

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_absolute_error

from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer
from sklearn.feature_extraction.text import CountVectorizer

from sklearn.linear_model import Lasso
from sklearn.model_selection import cross_val_score
from sklearn.externals import joblib

import pandas as pd
import numpy as np


import os
import sys
from subprocess import Popen
from random import randint

def process_list(df):
    to_flat = [
             'counciltax', 'crime',  'demographic', 'education',
             'employment', 'family', 'housing', 'interests', 'newspapers',
            ]

    for each in to_flat:
        new_added_df = pd.DataFrame(df[each].values.tolist()).add_prefix(each)
        df = pd.concat([df.drop(each, axis=1), new_added_df], axis=1, join='inner')
        
    return df

def get_meta(df):
    # basic preprocessing step
    meta = df.drop(["postcode", "price", "house_id", "description", "latitude", "longitude"], axis=1)
    meta = process_list(meta)
    meta = meta.fillna(0)
    meta = pd.get_dummies(meta)
    return meta

def load_model(name):
    return joblib.load(name)

def single_house_predict(house_id):
    # return file if it exists
    if os.path.isfile("%s.json" % house_id):
        return

    # start cralwer and wait until it finshes 
    p = Popen(["scrapy", "crawl", "single_spider",
               "-a", "house_id=%s" % house_id,
               "-o", "../web/static/assets/result/%s.json" % house_id],
              cwd="../../../../crawler/")
    p.wait()

    meta_model = load_model('meta_model')
    house = pd.read_json("%s.json" % house_id)
    train = pd.read_json("../../../../data/house.jl", lines=True)
    
    all_df = pd.concat([train, house], ignore_index=True)
    
    meta_house = get_meta(all_df)
    
    meta_pipe = Pipeline([('scaler', StandardScaler()), 
                          ('normalizer', Normalizer())])
    
    meta_house = meta_pipe.fit_transform(meta_house)
    
    
    meta = np.expm1(meta_model.predict(meta_house[-1:]))
    house.loc[:, 'prediction'] = (meta + house.price[0]) / 2
    house.loc[:, 'avg_sell'] = int((house.price[0] + house.prediction[0]) / 2)
    house.loc[:, 'avg_ask'] = int(house.avg_sell[0] - 24183)
    house.loc[:, 'price_max'] = house.prediction[0] + 30000
    house.loc[:, 'price_min'] = house.avg_ask[0] - 10000 
    if os.path.isfile("%s.result.json" % house_id):
        os.remove("%s.result.json" % house_id)
    pd.Series(house.loc[0]).to_json("%s.result.json" % house_id)


single_house_predict(sys.argv[1])
