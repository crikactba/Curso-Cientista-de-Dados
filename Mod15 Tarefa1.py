import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import time

st.set_page_config(page_title = 'SINASC Rondônia',
                    page_icon='https://upload.wikimedia.org/wikipedia/commons/e/ea/Flag_map_of_Rondonia.png',
                    layout='wide')

with st.spinner(text='Carregando... Aguarde!'):
    time.sleep(3)
    

def plota_pivot_table(df, value, index, func, ylabel, xlabel, opcao='nada'):
    if opcao == 'nada':# Opção de gráfico de linha simples sem agregações
        pd.pivot_table(df, values=value, index=index,
                       aggfunc=func).plot(figsize=[15, 5])
    elif opcao == 'sort': # Opção de gráfico de linha com ordenação especifica
        pd.pivot_table(df, values=value, index=index,
                       aggfunc=func).sort_values(value).plot(figsize=[15, 5])
    elif opcao == 'unstack': # Opção de grafico de linha com o eixo y contendo variaveis especificas
        pd.pivot_table(df, values=value, index=index,
                       aggfunc=func).unstack().plot(figsize=[15, 5])
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)

    st.pyplot(fig=plt)

    return None



st.title('Sistema de Informações sobre Nascidos Vivos - SINASC')
st.markdown("<h1 style='text-align: center; color: blue;'>Rondônia 2019</h1>", unsafe_allow_html=True)

sinasc = pd.read_csv('C:/Users/Cris/Documents/Python Scripts/Curso/input_M15_SINASC_RO_2019.csv')

#combobox:
selecao_selectbox = st.selectbox('Tipo do Gráfico:', ['Selecione uma opção','Média idade mãe por Data Nasc','Média idade mae por Sexo','Peso mediano do bebe pela Escolaridade da mae','Apgar1 medio por Gestação'])

sinasc.DTNASC = pd.to_datetime(sinasc.DTNASC)

min_data = sinasc.DTNASC.min()
max_data = sinasc.DTNASC.max()
#campos filtros de data:
data_inicial = st.sidebar.date_input('Data Inicial', 
                value = min_data,
                min_value = min_data,
                max_value = max_data)
data_final = st.sidebar.date_input('Data Final', 
                value = max_data,
                min_value = min_data,
                max_value = max_data)    


st.sidebar.write('Data Inicial = ', data_inicial)
st.sidebar.write('Data Final = ', data_final)


sinasc  = sinasc[(sinasc['DTNASC'] <= pd.to_datetime(data_final)) & (sinasc['DTNASC'] >=pd.to_datetime(data_inicial) )]

if selecao_selectbox == 'Média idade mãe por Data Nasc':
    plota_pivot_table(sinasc, 'IDADEMAE', 'DTNASC', 'mean', 'Média idade mãe', 'Data Nascimento')
elif selecao_selectbox == 'Média idade mae por Sexo':
    plota_pivot_table(sinasc, 'IDADEMAE', ['DTNASC', 'SEXO'], 'mean', 'Média idade mae','Data de Nascimento','unstack')
elif selecao_selectbox == 'Peso mediano do bebe pela Escolaridade da mae':
    plota_pivot_table(sinasc, 'PESO', 'ESCMAE', 'median', 'Peso mediano bebe','Escolaridade mae','sort')
elif selecao_selectbox == 'Apgar1 medio por Gestação':
    plota_pivot_table(sinasc, 'APGAR1', 'GESTACAO', 'mean', 'apgar1 medio','Gestacao','sort')
else:
    st.write('   ')