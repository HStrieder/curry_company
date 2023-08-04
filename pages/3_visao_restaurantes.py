#bibliotecas
from haversine import haversine 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import streamlit as st
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Restaurantes', page_icon='🍽️', layout='wide')

df = pd.read_csv('train.csv')

# Remover spaco da string
df['ID'] = df['ID'].str.strip()
df['Delivery_person_ID'] = df['Delivery_person_ID'].str.strip()

# Excluir as linhas com a idade dos entregadores vazia
# ( Conceitos de seleção condicional )
linhas_vazias = df['Delivery_person_Age'] != 'NaN '
df = df.loc[linhas_vazias, :]

# Conversao de texto/categoria/string para numeros inteiros
df['Delivery_person_Age'] = df['Delivery_person_Age'].astype( int )

# Conversao de texto/categoria/strings para numeros decimais
df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype( float )

# Conversao de texto para data
df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )

# Remove as linhas da culuna multiple_deliveries que tenham o
# conteudo igual a 'NaN '
linhas_vazias = df['multiple_deliveries'] != 'NaN '
df = df.loc[linhas_vazias, :]
df['multiple_deliveries'] = df['multiple_deliveries'].astype( int )

# Comando para remover o texto de números
df = df.reset_index( drop=True )

# Retirando os numeros da coluna Time_taken(min)
df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: x.split( '(min) ')[1])
df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)

# Retirando os espaços da coluna Festival
df['Festival'] = df['Festival'].str.strip()

df['City'] = df['City'].str.strip()

df['Road_traffic_density'] = df['Road_traffic_density'].str.strip()

# Remove os NAN da coluna City
df = df.loc[df['City']!='NaN']

df = df.loc[df['Weatherconditions'] != 'conditions NaN']

# Remove os NA que forem np.na
df = df.dropna()
df1 = df.copy()
df1['week_of_year'] = df1['Order_Date'].dt.strftime( "%U" )

#=======================================
#Barra Lateral
#=======================================
st.header('Marketplace - Visão Entregadores')
image_path = 'logo.png'
image = Image.open(image_path)
st.sidebar.image(image, width=120)

st.sidebar.markdown(' # Cury Company')
st.sidebar.markdown(' ## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown(' ## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime( 2022, 4, 13 ),
    min_value=datetime(2022, 2, 11 ),
    max_value=datetime(2022, 4, 6 ),
    format='DD-MM-YYYY' )


st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low','Medium','High', 'Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Striedious')

#============================
#Filtro de data
#============================
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]


#============================
#Layout streamlit
#============================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title("Overall Metrics")

        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            
           entregadores = len(df1.loc[:,'Delivery_person_ID'].unique())
           col1.metric( 'O número total de entregadores únicos é', entregadores )
            
        with col2:
            cols = ['Delivery_location_latitude','Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']

            df1['distance'] = (df1.loc[:, cols].apply(lambda x:
                          haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                                    (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1))
            avg_distance = np.round(df1['distance'].mean(),2)
            col2.metric('A distância média das entregas é', avg_distance)
            
        with col3:
            cols = ['Time_taken(min)', 'Festival']
            df_aux = df1.loc[:, cols].groupby('Festival').agg({'Time_taken(min)':['mean','std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'avg_time'],2)

            col3.metric('Tempo Médio de Entrega c/ Festival', df_aux)

        with col4:
            cols = ['Time_taken(min)', 'Festival']
            df_aux = df1.loc[:, cols].groupby('Festival').agg({'Time_taken(min)':['mean','std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'Yes', 'std_time'],2)

            col4.metric('Desvio Padrão Médio de Entrega c/ Festival', df_aux)

        with col5:
            cols = ['Time_taken(min)', 'Festival']
            df_aux = df1.loc[:, cols].groupby('Festival').agg({'Time_taken(min)':['mean','std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'No', 'avg_time'],2)

            col5.metric('Tempo Médio de Entrega c/ Festival', df_aux)

            

        with col6:
            cols = ['Time_taken(min)', 'Festival']
            df_aux = df1.loc[:, cols].groupby('Festival').agg({'Time_taken(min)':['mean','std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            df_aux = np.round(df_aux.loc[df_aux['Festival'] == 'No', 'std_time'],2)

            col6.metric('Desvio Padrão Médio de Entrega c/ Festival', df_aux)
        
    with st.container():

        cols = ['City', 'Time_taken(min)']
        df_aux = df1.loc[:, cols].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
        df_aux.columns = ['avg_time','std_time']
        df_aux = df_aux.reset_index()

        fig = go.Figure()
        fig.add_trace(go.Bar( name='Control', x=df_aux['City'], y=df_aux['avg_time'],error_y=dict(type='data', array=df_aux['std_time'])))
        fig.update_layout(barmode='group')
        st.plotly_chart(fig, use_container_width=True)
        
        
        
    with st.container():
        st.markdown("# Distribuição do Tempo")
       
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### Tempo Médio de entrega por cidade")
            cols = ['Delivery_location_latitude','Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']

            df1['distance'] = (df1.loc[:, cols].apply(lambda x:
                              haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                                        (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1))
            avg_distance = df1.loc[:,['City', 'distance']].groupby('City').mean().reset_index()
            fig = go.Figure( data=[ go.Pie( labels=avg_distance['City'], values=avg_distance['distance'], pull=[0,0.1,0])])
            st.plotly_chart(fig, use_container_width=True)



        with col2:
            st.markdown("##### Tempo Médio de entrega por cidade")
            df_aux = (df1.loc[:,['City', 'Time_taken(min)','Road_traffic_density']]
                      .groupby(['City', 'Road_traffic_density'])
                      .agg({'Time_taken(min)':['mean','std']}))
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                              color='std_time', color_continuous_scale='RdBu',
                              color_continuous_midpoint=np.average(df_aux['std_time']))
            st.plotly_chart(fig, use_container_width=True)
        

    with st.container():
        
        st.title("Distribuição da Distância")   

        cols = ['City', 'Time_taken(min)','Type_of_order']

        dfaux = df1.loc[:, cols].groupby(['City','Type_of_order']).agg({'Time_taken(min)':{'mean', 'std'}})
        dfaux.columns = ['avg_time','std_time']
        dfaux.reset_index()
        st.dataframe(dfaux, use_container_width=True)
 
