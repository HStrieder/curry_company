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

st.set_page_config(page_title='Visão Empresa', page_icon='📈', layout='wide')

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

#=======================================
#LAYOUT STREAMLIT - Barra Lateral
#=======================================
st.header('Marketplace - Visão Cliente')
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

#Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

#===========================
# Layout no Streamlit
#===========================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        #quantidade de pedidos por dia
        st.markdown('# Orders by day')
        df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby( 'Order_Date' ).count().reset_index()
        df_aux.columns = ['order_date', 'qtde_entregas']
        
        # gráfico
        
        st.plotly_chart(px.bar( df_aux, x='order_date', y='qtde_entregas' ), use_container_width=True )

    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            
            st.markdown('# Traffic Order Share')
            columns = ['ID', 'Road_traffic_density']
            df_aux = df1.loc[:, columns].groupby( 'Road_traffic_density' ).count().reset_index()
            df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
            # gráfico
            st.plotly_chart(px.pie( df_aux, values='perc_ID', names='Road_traffic_density'), use_container_width=True )
            
        with col2:
            
            st.markdown('# Traffic Order City')
            df_aux = df1.loc[:,['ID','City','Road_traffic_density']].groupby(['City','Road_traffic_density']).count().reset_index()
            df_aux = df_aux.loc[df_aux['City'] != 'NaN',:]
            df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN',:]

            fig = px.scatter( df_aux, x='City', y='Road_traffic_density', size ='ID', color='City')
            st.plotly_chart(fig, use_container_width=True)

    
with tab2:
    
    with st.container():
        st.markdown('# Order by Week')
        df1['week_of_year'] = df1['Order_Date'].dt.strftime("%U")
        df_aux = df1.loc[:,['ID','week_of_year']].groupby('week_of_year').count().reset_index()
        # gráfico
        fig = px.line( df_aux, x='week_of_year', y='ID' )
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown('# Order Share by Week')
        df_aux1 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
        df_aux2 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby( 'week_of_year').nunique().reset_index()
        df_aux = pd.merge( df_aux1, df_aux2, how='inner' )
        df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
        # gráfico
        fig = px.line( df_aux, x='week_of_year', y='order_by_delivery' )
        st.plotly_chart(fig, use_container_width=True)
        
with tab3:
    st.markdown('# Country Maps')
        
    columns = [
    'City',
    'Road_traffic_density',
    'Delivery_location_latitude',
    'Delivery_location_longitude'
    ]
    columns_grouped = ['City', 'Road_traffic_density']
    data_plot = df1.loc[:, columns].groupby( columns_grouped ).median().reset_index()
    data_plot = data_plot[data_plot['City'] != 'NaN']
    data_plot = data_plot[data_plot['Road_traffic_density'] != 'NaN']
    # Desenhar o mapa
    map = folium.Map( zoom_start=11 )
    for index, location_info in data_plot.iterrows():
      folium.Marker( [location_info['Delivery_location_latitude'],
                      location_info['Delivery_location_longitude']],
                    popup=location_info[['City', 'Road_traffic_density']] ).add_to( map )
    folium_static( map, width=1024 , height=600 )
