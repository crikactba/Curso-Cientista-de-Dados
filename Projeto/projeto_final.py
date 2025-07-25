import pandas            as pd
import streamlit         as st
import numpy             as np
from datetime import date

#import seaborn as sns
#import matplotlib.pyplot as plt

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import FunctionTransformer

import pickle

from pycaret.classification import *
from pycaret.datasets import get_data
from pycaret.classification import setup


def options_form():
    with st.sidebar.form('Opções do Modelo'):
        file = st.file_uploader('Upload', type=['ftr'])
        st.header('Opções do Modelo')
        model_type = st.radio('Classifier type', [
            'lr',
            'lightgbm',
        ])
        sample_size = st.slider('Sample size', 0.0, 1.0, .1)
        fold = st.slider('Number of folds', 3, 20, 5)
        tune_model = st.checkbox('Tune model', False)
        form_updated = st.form_submit_button('Train')

        return {
            'updated': form_updated,
            'file': file,
            'model_type' : model_type, 
            'sample_size': sample_size,
            'tune_model' : tune_model,
            'fold': fold,
        }

def init_data(data = None, split = False):
    
    data = pd.read_feather(data).dropna()
    #data.dropna(inplace=True)

    data['safra'] = (data['data_ref'].dt.year - min(data['data_ref'].dt.year))*12 + data['data_ref'].dt.month
    data = data.reindex(columns=['renda'] + [col for col in data.columns if col != 'renda'])
    if not split: 
        return data
    df_train = data[data.safra <= 12]
    df_test = data[data.safra > 12]
    return {
         'train': df_train,
         'test': df_test,
    }

def setup_pycaret(data, fold=5):

    #log_renda_trans = ColumnTransformer([('log_renda', FunctionTransformer(np.log), ['renda'])], remainder='passthrough')

    return setup(
        data=data, 
        target='mau',
        numeric_imputation='mean',
        ignore_features=['index', 'data_ref', 'safra'],
        max_encoding_ohe=-1,
        remove_outliers=True,
        outliers_method='lof',
        pca=True,
        pca_components=5,
        normalize=True,

        feature_selection=False,
        feature_selection_method='classic',

        #custom_pipeline=Pipeline([('log_renda', log_renda_trans)]),
        #custom_pipeline_position=0,
        fold_strategy='timeseries',
        fold=5,
        data_split_shuffle=False, 
        fold_shuffle=False,
        data_split_stratify=False
        
    )

def train_model(model_type):
    return create_model(model_type)

def calibrate_model(_clf):
    return tune_model(_clf, fold=3)

def inspect_model(clf, plot_type):
    plot_model(clf, plot_type, display_format='streamlit')
    #evaluate_model(clf, plot_kwargs={'display_format': 'streamlit'})

def wrap_model(_clf):
    return finalize_model(_clf)

def deserialize_model(data):
    return pickle.loads(data)

def serialize_model(clf):
    return pickle.dumps(clf)

def main():

    title = 'Análise de Crédito'

    st.set_page_config(page_title = title, 
        initial_sidebar_state='auto',
        layout="wide",
    )

    st.title(title)

    options = options_form()
    file = options['file']
    if not file:
        st.sidebar.info('Carregue o arquivo .ftr!')
        st.stop()

    data = init_data(file)

    if options['sample_size'] < 1.0:
        data = data.sample(frac=options['sample_size'])

    if options['updated']:
        st.session_state['exp'] = setup_pycaret(data, fold=options['fold'])
        st.session_state['clf'] = train_model(options['model_type'])
        if options['tune_model']:
            st.session_state['clf'] = calibrate_model(st.session_state['clf'])
        st.session_state['final_clf'] = wrap_model(st.session_state['clf'])

    if ('exp' not in st.session_state):
        st.sidebar.info('Selecione o tipo do modelo e clique em **Train**')
        st.stop()

    st.header('Estatísticas do modelo')

    plot_type = st.radio('Tipo:', [
        'auc',
        'pr',
        'confusion_matrix',
    ])
    inspect_model(st.session_state['clf'], plot_type)

    st.header('Download do modelo final')
    
    clf_bytes = serialize_model(st.session_state['final_clf'])
    st.download_button('Download model', clf_bytes, f'final_credit_clf_ {date.today()}.pkl')
        

if __name__ == '__main__':
	main()
