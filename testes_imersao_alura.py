from matplotlib.pylab import eig
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mplfinance as mpf
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
pd.options.display.float_format = '{:.2f}'.format

############################# Tratamento dos Dados ###################################

df_principal = pd.read_excel('imersao_python_tabela_acoes.xlsx', sheet_name="Principal")
df_total_acoes = pd.read_excel('imersao_python_tabela_acoes.xlsx', sheet_name="Total_de_acoes")
df_ticker = pd.read_excel('imersao_python_tabela_acoes.xlsx', sheet_name= "Ticker")
df_gepeto = pd.read_excel('imersao_python_tabela_acoes.xlsx', sheet_name= "Gepeto")
df_principal = df_principal[['Ativo',	'Data',	'Último (R$)',	'Var. Dia (%)']].copy()
#print(df_principal)

df_principal = df_principal.rename(columns={'Último (R$)': 'valor_final', 'Var. Dia (%)':'var_dia_pct'}).copy()
#print(df_principal)

df_principal['var_pct'] = df_principal['var_dia_pct'] / 100
df_principal['valor_inicial'] = df_principal['valor_final'] / (df_principal['var_pct']+1)

df_principal = df_principal.merge(df_total_acoes, left_on='Ativo', right_on='Código', how='left')
#esse .merge é igual ao PROCV/VLookUp, estou 'mesclando' na tabela principal uma nova coluna, sendo ela de acordo com o q tem no ativo, puxando o q está no outro dataframe(planilha), o código representando
#print(df_principal)

df_principal = df_principal.drop(columns=['Código'])
#print(df_principal)

df_principal['variacao_rs'] = (df_principal['valor_final'] - df_principal['valor_inicial']) * df_principal['Qtde. Teórica']
df_principal['Qtde. Teórica'] = df_principal['Qtde. Teórica'].astype(int)
df_principal = df_principal.rename(columns={'Qtde. Teórica': 'qtde_teorica'}).copy()
#print(df_principal)

df_principal['resultado'] = df_principal['variacao_rs'].apply(lambda x: 'Subiu' if x>0 else ('Desceu' if x<0 else 'Estavel'))
#a função apply é uma função para chamar outras funções. Ou seja, aplicando um chamador de funções para a coluna, o Lambda é usado para operações linha a linha, ou seja, definindo uma função para aplicar linha a linha
#print(df_principal)

df_principal = df_principal.merge(df_ticker, left_on='Ativo', right_on='Ticker', how='left')
df_principal = df_principal.drop(columns=['Ticker'])
#print(df_principal)

df_principal = df_principal.merge(df_gepeto, left_on='Nome', right_on='Nome Empresa', how='left')
df_principal = df_principal.drop(columns=['Nome'])
#print(df_principal)

df_principal = df_principal.rename(columns={'Idade (anos)': 'idade'})
df_principal['cat_idade'] = df_principal['idade'].apply(lambda x: 'Mais que 100 anos' if x>100 else ('Menos que 50 anos' if x<50 else 'Entre 50 e 100 anos'))
print(df_principal)


############################# Análise dos Dados #####################################
#Calculo dos valores brutos

maior = df_principal['variacao_rs'].max()
menor = df_principal['variacao_rs'].min()
media = df_principal['variacao_rs'].mean()

#Cálculo das médias
media_subiu = df_principal[df_principal['resultado'] == 'Subiu']['variacao_rs'].mean()
#aqui estou pegando todos os resultados que contém Subiu e calculando a média deles
media_desceu = df_principal[df_principal['resultado'] == 'Desceu']['variacao_rs'].mean()
#o mesmo resultado de cima, porém de quem Desceu

print(f'Maior\tR${maior:,.2f}')
print(f'Menor\tR${menor:,.2f}')
print(f'Media\tR${media:,.2f}')
print(f'Média de quem subiu\tR${media_subiu:,.2f}')
print(f'Média de quem desceu\tR${media_desceu:,.2f}')

df_principal_subiu = df_principal[df_principal['resultado'] == 'Subiu']
#aqui estou criando um dataframe somente para os resultados que subiram

#análise de variação por segmento dos que subiram
df_analise_segmento = df_principal_subiu.groupby('Segmento')['variacao_rs'].sum().reset_index()
#reset index é pq, se utilizar somente o groupby, ele irá vetorizar minha tabela alterando o tipo do dado. O reset_index irá manter o tipo de dado

print(df_analise_segmento)

df_analise_saldo = df_principal.groupby('resultado')['variacao_rs'].sum().reset_index()
print(df_analise_saldo)

##################################### Criação de Gráficos ##################################

#fig = px.bar(df_analise_saldo, x='resultado', y='variacao_rs', text='variacao_rs', title='Variação Reais por Resultado')
#print(fig.show())


############ Biblioteca YFinance (YAHOO FINANCE - Biblioteca da bolsa de valores) ##########


dados = yf.download('PETR4.SA', start='2023-01-01', end='2023-12-31')
dados.columns = ['Abertura', 'Maximo', 'Minimo', 'Fechamento', 'Fech_Ajust', 'Volume']
dados = dados.rename_axis('Data')
#print(dados)

dados['Fechamento'].plot(figsize=(10,6))
#plotar algo é 'mostrar' o gráfico ou algo q estamos plotando
plt.title('Variação do Preço por Data', fontsize=16)
plt.legend(['Fechamento'])
#aqui estou criando o gráfico (não aparece no vscode, mas pelo google colab vai)

df = dados.head(60).copy()
#criação de um novo dataframe sendo uma copia do principal c apenas as 60 primeiras linhas
df['Data'] = df.index
#aqui estou criando uma nova coluna que vai pegar a data index (duplicando a primeira linha do df)
#convertendo as datas para formato numérico de matplotlib
#é necessário para que o matplotlib possa plotar as datas corretamente no gráfico
df['Data'] = df['Data'].apply(mdates.date2num)

print(df)

#criação do grafico candlestick (grafico de velas)
eig, ax= plt.subplots(figsize=(15, 8))
width=0.7
#agora vem a definição das cores das velas
for i in range(len(df)):
    if df['Fechamento'].iloc[i] > df['Abertura'].iloc[i]:
        #esse [i] é o item do for, ou seja, a cada iteração vai determinar a cor de cada vela
        color = 'green'
    else:
        color = 'red'

    #desenhando a linha vertical do candle(mecha)
    #essa linha mostra os preços máximos e mínimos do dia
    #usamos ax.plot para desenhar a linha vertical (q vai servir de base pras velas)
    #
    ax.plot([df['Data'].iloc[i], df['Data'].iloc[i]],
            [df['Minimo'].iloc[i], df['Maximo'].iloc[i]],
            color = color,
            linewidth=1)
    
    ax.add_patch(plt.Rectangle((df['Data'].iloc[i] - width/2, min(df['Abertura'].iloc[i], df['Fechamento'].iloc[i])),
                               width,
                               abs(df['Fechamento'].iloc[i] - df['Abertura'].iloc[i]),
                               facecolor= color))


df['MA7'] = df['Fechamento'].rolling(window=7).mean()
df['MA14'] = df['Fechamento'].rolling(window=14).mean()

#plotando as médias moveis
ax.plot(df['Data'], df['MA7'], color='orange', label='Média Móvel 7 Dias')
ax.plot(df['Data'], df['MA14'], color='yellow', label='Média Móvel 14 Dias')
#aplicando legendas para as médias moveis
ax.legend()

#formatando o eixo x para mostrar as datas
#configurando o formato da data e a rotação para melhor legibilidade
ax.xaxis_date() #o método xaxis_date() é usado para dizer ao matplotlib que as datas estão sendo usadas no eixo X
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.xticks(rotation=45)

#adicionando títulos e rótulos para os eixos x e y
plt.title("Gráfico de Candlestick - PETR4.SA com MatPlotLib")
plt.xlabel("Data")
plt.ylabel("Preço")

#adicionando uma grade para facilitar a visualização dos valores

plt.grid(True)

#exibindo o gráfico
print(plt.show())


################################ CRIAÇÃO DE SUBPLOTS ############################################
'''
Primeiro, criamos uma figura que conterá nossos gráficos usando make_subplots.
Isso nos permite ter múltiplos gráficos em uma única visualização.
Aqui, teremos dois subplots: um para o gráfico candlestick e outro para o volume de transações

'''
fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                    vertical_spacing=0.1,
                    subplot_titles=('Candlesticks', 'Volume Transacionado'),
                    row_width=[0.2, 0.7])                  

'''
No gráfico candlestick, cada vela representa um dia de negociação, mostrando o preço de abertura, fechamento, máximo e mínimo. Vamos adicionar esse gráfico a nossa figura
'''

#Adicionando o gráfico de candlestick

fig.add_trace(go.Candlestick(x=df.index,
                             open=df['Abertura'],
                             high=df['Maximo'],
                             low=df['Minimo'],
                             close=df['Fechamento'],
                             name='Candlestick'),
                             row=1, col=1)

#Adicionando as médias móveis
#Adicionamos também as médias móveis ao mesmo subplot para análise de tendências
fig.add_trace(go.Scatter(x=df.index,
                         y=df['MA7'],
                         mode='lines',
                         name= 'MA7 - Média Móvel 07 Dias'),
                         row=1, col=1)

fig.add_trace(go.Scatter(x=df.index,
                         y=df['MA14'],
                         mode='lines',
                         name='MA14 - Média Móvel 14 Dias'),
                         row=1, col=1)


#Adicionando o gráfico de barras para o volume
#Em seguida, criamos um gráfico de barras para o volume de transações, que nos dá uma ideia da atividade de negociação daquele dia
fig.add_trace(go.Bar(x=df.index,
                     y=df['Volume'],
                     name='Volume'),
                     row=2, col=1)

#Atualizando o layout
#Finalmente, configuramos o layout da figura, ajustando títulos, formatos de eixos e outras configurações para tornar o gráfico mais legível 
fig.update_layout(yaxis_title='Preço',
                  xaxis_rangeslider_visible=False, #desativa o range slider
                  width=1100, height=600)

print(fig.show())


dadoss = yf.download('PETR4.SA', start='2023-01-01', end='2023-12-31')
mpf.plot(dadoss.head(30), type='candle', figsize=(16, 8), mav=(7,14), style='yahoo')
print(dadoss.show())



