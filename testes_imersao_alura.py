import pandas as pd

pd.options.display.float_format = '{:.2f}'.format

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
print(df_principal)