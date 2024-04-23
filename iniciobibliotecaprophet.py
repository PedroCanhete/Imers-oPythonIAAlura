import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from prophet import Prophet

dados = yf.download("JNJ", start='2020-01-01', end= '2023-12-31', progress=False)
dados = dados.reset_index()
'''print(dados)'''

#Separação de dados para utilizar o Machine Learning (dados p máquina treinar e outros para testar)
dados_treino = dados[dados['Date'] < '2023-07-31']
dados_teste = dados[dados['Date'] >= '2023-07-31']


#preparação dos dados p FBProphet
dados_prophet_treino = dados_treino[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close':'y'})
'''print(dados_prophet_treino)'''

#Criação e treinamento de modelo
modelo = Prophet(weekly_seasonality=True,
                 yearly_seasonality=True,
                 daily_seasonality=False)
#seasonanily é um 'comando' p indicar ao dataframe que podem ocorrer alterações semanais e anuais, diárias deixamos sem, mas depende do caso
modelo.add_country_holidays(country_name='US')
#comando p dataframe levar em consideração os feriados, no caso, como a base é americana, usando os feriados dos EUA
modelo.fit(dados_prophet_treino)
#.fit é um comando p mandar o meu modelo treinar/aprender

#criação de datas futuras p previsão até o fim do ano de 2023 (ano final do df que estou utilizando)
futuro = modelo.make_future_dataframe(periods=150)
previsao = modelo.predict(futuro)


#plotando os dados de treino, teste e previsões
plt.figure(figsize=(14, 8))
plt.plot(dados_treino['Date'], dados_treino['Close'], label='Dados de Treino', color='blue')
plt.plot(dados_teste['Date'], dados_teste['Close'], label='Dados Reais (Teste)', color='green')
plt.plot(previsao['ds'], previsao['yhat'], label='Previsão', color='orange', linestyle='--')

plt.axvline(dados_treino['Date'].max(), color='red', linestyle='--', label='Início da Previsão')
plt.xlabel('Data')
plt.ylabel('Preço de Fechamento')
plt.title('Previsão de Preço de Fechamento vs Dados Reais')
plt.legend()
print(plt.show())
