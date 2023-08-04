#bibliotecas
from haversine import haversine 
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Entregadores', page_icon='🚚', layout='wide')

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
#Filtro de transito
#============================
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options)
df1 = df1.loc[linhas_selecionadas, :]


#===========================
# Layout no Streamlit
#===========================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        
        col1,col2,col3,col4 = st.columns(4 , gap='large')
        with col1:
            st.title('Maior Idade')
            #A maior idade dos entregadores
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior idade', maior_idade)

        with col2:
            st.title('Menor de idade')
            menor_idade = df1.loc[:,'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)

        with col3:
            st.title('Melhor condição de veiculos')
            condicao = df1.loc[:,"Vehicle_condition"].max()
            col3.metric('A Melhor condição', condicao)

        with col4:
            st.title('Pior condição de veiculos')
            condicao = df1.loc[:,"Vehicle_condition"].min()
            col4.metric('A Pior condição', condicao)
            
    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Avaliações Médias por Entregador')
            avaliacoes_medias = df1[['Delivery_person_ID', 'Delivery_person_Ratings']].groupby('Delivery_person_ID').mean().reset_index()
            st.dataframe(avaliacoes_medias)
            
        with col2:
            st.subheader('Avaliação Média por trânsito')
            avaliacoes_trafico = (df1.loc[:,['Road_traffic_density', 'Delivery_person_Ratings']]
                                  .groupby('Road_traffic_density')
                                  .agg({'Delivery_person_Ratings':['mean', 'std']}))
            avaliacoes_trafico.columns = ['delivery_mean','delivery_std']
            avaliacoes_trafico = avaliacoes_trafico.reset_index()
            st.dataframe(avaliacoes_trafico)
            
            
            st.subheader('Avaliação Média por clima')
            avaliacoes_clima = (df1.loc[:,['Weatherconditions', 'Delivery_person_Ratings']]
                                .groupby('Weatherconditions')
                                .agg({'Delivery_person_Ratings': ['mean','std']}))
            avaliacoes_clima.columns = ['delivery_mean','delivery_std']
            avaliacoes_clima = avaliacoes_clima.reset_index()
            st.dataframe(avaliacoes_clima)

                        

    with st.container():
        st.header('Velocidade de Entrega')
        col1, col2 = st.columns(2)

        with col1:
            st.subheader('Top Entregadores mais rápidos')
            df2 = (df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                   .groupby(['City','Delivery_person_ID'])
                   .mean()
                   .sort_values( ['City','Time_taken(min)'], ascending=True ).reset_index())

            df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
            df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
            df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

            df3 = pd.concat([df_aux01 ,df_aux02,df_aux03]).reset_index(drop=True)
            st.dataframe(df3)


        with col2:
            st.subheader('Top Entregadores mais lentos')
            df2 = (df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                   .groupby(['City','Delivery_person_ID'])
                   .mean()
                   .sort_values( ['City','Time_taken(min)'], ascending=False ).reset_index())

            df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
            df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
            df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

            df3 = pd.concat([df_aux01 ,df_aux02,df_aux03]).reset_index(drop=True)
            st.dataframe(df3)

            