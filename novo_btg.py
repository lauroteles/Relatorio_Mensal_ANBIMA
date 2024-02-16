import pandas as pd
import numpy as np
import openpyxl as op
import streamlit as st
import os
from datetime import datetime


class Anbima_mensal():

    def __init__(self,caminho_dados):
        os.chdir(caminho_dados)

    def btg(caminho_controle,caminho_base_clientes,caminho_rentabilidade):

        controle = pd.read_excel(caminho_controle,1,skiprows=1)
        base_de_clientes = pd.read_excel(caminho_base_clientes)
        rentabilidade = pd.read_excel(caminho_rentabilidade,skiprows=1)

        base_de_clientes = base_de_clientes[['Retiradas', 'Aportes', 'PL Total',
                        'Fundos', 'Perfil do Cliente','Conta']]

        controle = controle[['Conta', 'Status','Início da Gestão',  'Data distrato',
                            'Carteira','Taxa de Gestão', 'Benchmark TX. Perf', 'TX. Perf.']]

        rentabilidade = rentabilidade[['Conta', 'Rentabilidade',]]

        controle['Conta'] = controle['Conta'].astype(str).apply(lambda x: '00'+x).str[:-2]
        controle = controle.iloc[:-5,:]
        btg_final = pd.merge(controle,rentabilidade,on='Conta',how='outer')
        btg_final = btg_final.merge(base_de_clientes,on='Conta',how='outer').reset_index().drop(columns='index').iloc[:-1,:]
        return btg_final

    def guide(caminho_dos_arquivos_controle,caminho_dos_arquivos_patrimonio,caminho_dos_arquivos_fundos,caminho_dos_arquivos_mes_anterior,caminho_aportes_resg):

        controle = pd.read_excel(caminho_dos_arquivos_controle,2,skiprows=1)
        patrimio_liquido = pd.read_excel(caminho_dos_arquivos_patrimonio)
        fundos = pd.read_excel(caminho_dos_arquivos_fundos)
        patrimonio_liquid_mes_anterior = pd.read_excel(caminho_dos_arquivos_mes_anterior)
        aportes_e_resgates = pd.read_excel(caminho_aportes_resg)

        patrimio_liquido = patrimio_liquido[['CLIE_ID','SALDO_BRUTO']].groupby('CLIE_ID')['SALDO_BRUTO'].sum().reset_index().rename(columns={'CLIE_ID':'Conta',
                                                                                                                                            'SALDO_BRUTO':'PL Total Atual'})
        patrimio_liquido['Conta'] = patrimio_liquido['Conta'].astype(str)

        fundos = fundos[['CLIE_ID', 'MERCADO','SALDO_BRUTO',]].groupby(['CLIE_ID','MERCADO'])['SALDO_BRUTO'].sum().reset_index().rename(columns={'CLIE_ID':'Conta',
                                                                                                                                                'SALDO_BRUTO':'Valor_em_Fundos'})
        fundos= fundos.loc[fundos['MERCADO']=='FD']
        fundos['Conta'] = fundos['Conta'].astype(str)

        patrimonio_liquid_mes_anterior = patrimonio_liquid_mes_anterior[['CLIE_ID','SALDO_BRUTO']].groupby('CLIE_ID')['SALDO_BRUTO'].sum().reset_index().rename(columns={'CLIE_ID':'Conta',
                                                                                                                                                                        'SALDO_BRUTO':'PL_MES_ANTERIOR'})
        patrimonio_liquid_mes_anterior['Conta'] = patrimonio_liquid_mes_anterior['Conta'].astype(str)

        controle = controle[['Conta','Status','Início da Gestão', 'Data distrato',
                            'Carteira','Taxa de Gestão','Benchmark TX.  Perf.','TX. Perf.']].iloc[:-5,:]
        controle['Conta'] = controle['Conta'].astype(str).str[:-1]


        aportes_e_resgates = aportes_e_resgates[['Cod. Conta Local','Valor','Descricao']]

        descricao_aportes_e_resgates = [ 'Liquidação','TED','RESGATE','TRANSFERENCIA','COMPRA','APLICAÇÃO']

        ted = aportes_e_resgates[aportes_e_resgates['Descricao'].astype(str).str.contains('TED')]

        filtrado_aportes_e_resgates=[]
        for descricao in descricao_aportes_e_resgates:
            df = aportes_e_resgates[aportes_e_resgates['Descricao'].astype(str).str.contains(descricao)]
            filtrado_aportes_e_resgates.append(df)


        aportes_e_resgates_df = pd.concat(filtrado_aportes_e_resgates)
        aportes_e_resgates_df = aportes_e_resgates_df.groupby('Cod. Conta Local')['Valor'].sum().reset_index()
        resgates = aportes_e_resgates_df.loc[aportes_e_resgates_df['Valor']<0]
        aportes = aportes_e_resgates_df.loc[aportes_e_resgates_df['Valor']>0]
        aportes_e_resgates_df = aportes_e_resgates_df.merge(resgates,on='Cod. Conta Local',how='outer').merge(aportes,on='Cod. Conta Local',how='outer').rename(columns={
            'Cod. Conta Local':'Conta','Valor_y':'Retiradas','Valor':'Aportes'}).drop(columns='Valor_x')
        aportes_e_resgates_df['Conta'] = aportes_e_resgates_df['Conta'].astype(str)

        guide_final = controle.merge(patrimio_liquido,on='Conta',how='outer').merge(patrimonio_liquid_mes_anterior,on='Conta',how='outer').merge(fundos,on='Conta',how='outer').merge(aportes_e_resgates_df,on='Conta',how='outer')
        colunas_preencher_0 = ['Retiradas','Aportes','PL_MES_ANTERIOR','PL Total Atual']
        guide_final[colunas_preencher_0] = guide_final[colunas_preencher_0].fillna(0)
        guide_final['Rentabilidade'] = (((guide_final['PL Total Atual'] - guide_final['Aportes'])+guide_final['Retiradas'])-guide_final['PL_MES_ANTERIOR'])/guide_final['PL_MES_ANTERIOR']*100
        guide_final = guide_final.drop(columns=['PL_MES_ANTERIOR','MERCADO']).rename(columns={'PL Total Atual':'PL Total',
                                                                                            'Valor_em_Fundos':'Fundos',
                                                                                            })
        return guide_final

    def padronizando_dados(btg_final,guide_final,filtro_data):
        arquivo_final = pd.concat([btg_final,guide_final]).reset_index().drop(columns='index')
        coluna_para_retirar =['Não começou','-','ENCERRADA',]
        arquivo_final = arquivo_final[~arquivo_final['Início da Gestão'].isin(coluna_para_retirar)]

        arquivo_final['Início da gestao'] = pd.to_datetime(arquivo_final['Início da Gestão'])
        arquivo_final = arquivo_final[arquivo_final['Início da gestao']< pd.to_datetime(filtro_data)]

        arquivo_final['Início da Gestão'] = pd.to_datetime(arquivo_final['Início da Gestão']).dt.strftime("%d/%m/%Y")
        arquivo_final['Data distrato'] = pd.to_datetime(arquivo_final['Data distrato']).dt.strftime("%d/%m/%Y")

        ajustando_perfil_carteira = {
                        'CON':'Conservadora',  'CORP':'Conservadora', 'CRIP':'Arrojada',  'DIV':'Arrojada',
                        'EQT':'Arrojada',  'FII':'Arrojada',  'FUND':'Moderada',
                        'MONT':'Conservadora',  'PREV':'Conservadora',   'SMLL':'Arrojada',
                        'MOD':'Moderada',  'INC':'Conservadora',   'MLT MAC':'Arrojada',   'ARR' : 'Arrojada'
                        }
        arquivo_final['Carteira'] = arquivo_final['Carteira'].replace(ajustando_perfil_carteira,regex=True)

        adicionar_colunas = [
            'Codigo ANBIMA','Modelo da carteira', 'Seguemento do investidor',
            'Publico Alvo','Permite Credito Privado','Permite investimento no exterior', 'Permite Investintos em cotas','Permite Derivativos', 'Estrategias permitidas com derivativos',
            'Tipo da taxa de gestao', 'Descricao da taxa de gestao', 'Cobranca da taxa complementar', 'Tipo de cobranca de taxa complementar', 'Valor da taxa complementar',
                'Tipo de cobranca da taxa de performance','Taxa de performance', 'Descricao da taxa de performance','Descrição da taxa complementar','Cobranca da taxa de performance',
            'Utiliza benchmark.1','Possui custodiante contratado', 'CNPJ do custodiante contratado','Possui controlador contratado', 'CNPJ do controlador contratado',
            'O apreçamento da carteira é realizado pelo [GESTOR ou TERCEIRO CONTRATADO]','CNPJ do responsavel pelo aprecamento','Permite Criptomoeda','Campo de Apoio' ]
        for colunas in adicionar_colunas:
            arquivo_final[colunas] = ''
            

        arquivo_final = arquivo_final[['Codigo ANBIMA', 'Conta', 'Status', 'Início da Gestão', 'Data distrato','Modelo da carteira', 'Seguemento do investidor', 'Publico Alvo', 'Carteira',
            'Perfil do Cliente', 'Permite Credito Privado',   'Permite investimento no exterior', 'Permite Investintos em cotas', 'Permite Derivativos', 'Estrategias permitidas com derivativos',
            'Tipo da taxa de gestao', 'Taxa de Gestão', 'Descricao da taxa de gestao', 'Cobranca da taxa complementar', 'Tipo de cobranca de taxa complementar', 'Valor da taxa complementar',
            'Descrição da taxa complementar', 'Cobranca da taxa de performance', 'Tipo de cobranca da taxa de performance', 'TX. Perf.', 'Descricao da taxa de performance',  'Utiliza benchmark.1', 'Benchmark TX. Perf',
            'Possui custodiante contratado', 'CNPJ do custodiante contratado',  'Possui controlador contratado', 'CNPJ do controlador contratado', 'O apreçamento da carteira é realizado pelo [GESTOR ou TERCEIRO CONTRATADO]',
            'CNPJ do responsavel pelo aprecamento', 'Rentabilidade', 'Aportes', 'Retiradas', 'PL Total',  'Fundos', 'Permite Criptomoeda',  'Campo de Apoio' 
            ]]

        valores_padrao = {
            'Modelo da carteira' : 'Padronizada',
            'Seguemento do investidor' : 'Varejo',
            'Publico Alvo' : 'Investidores em geral',
            'Permite Credito Privado': 'Sim',
            'Permite investimento no exterior':'Não',
            'Permite Investintos em cotas':'Sim',
            'Permite Derivativos':'Sim',
            'Estrategias permitidas com derivativos':'Hedge,Posicionamento',
            'Tipo da taxa de gestao':'Percentual',
            'Cobranca da taxa complementar':'Não',
            'CNPJ do responsavel pelo aprecamento':'09.722.735/0001-01',
            'O apreçamento da carteira é realizado pelo [GESTOR ou TERCEIRO CONTRATADO]':'Própria',
            'Possui controlador contratado':'Não',
            'Possui custodiante contratado':'Não',
            'Permite Criptomoeda':'Permite indiretamente'
        }

        for coluna, valor in valores_padrao.items():
            arquivo_final[coluna] = valor

        arquivo_final['TX. Perf.'] = ''
        arquivo_final['Benchmark TX. Perf'] = arquivo_final['Benchmark TX. Perf'].str.replace('IBOV','IBOVESPA')
        conditicoes = [arquivo_final['Benchmark TX. Perf'] == 'IBOVESPA',arquivo_final['Benchmark TX. Perf'] ==  'CDI',
                    arquivo_final['Benchmark TX. Perf'] ==  'IFIX',arquivo_final['Benchmark TX. Perf'] ==  'S&P 500']

        escolhas = ['O que exceder o IBOVESPA','O que exceder o CDI','O que exceder IFIX','O que exceder o S&P 500']

        percent = [ arquivo_final['Cobranca da taxa de performance'] == 'Sim']
        percentual = [ 'Percentual']

        arquivo_final['Descricao da taxa de performance'] = np.select(conditicoes,escolhas,default='')
        arquivo_final['Tipo de cobranca da taxa de performance'] = np.select(percent,percent,default='')      
        arquivo_final['Tipo de cobranca da taxa de performance'] = arquivo_final['Tipo de cobranca da taxa de performance'].str.replace('True','Percentual')
        arquivo_final['Benchmark TX. Perf'] = arquivo_final['Benchmark TX. Perf'].str.replace('------','').str.replace('----','')
        arquivo_final['Utiliza benchmark.1'] = arquivo_final['Benchmark TX. Perf'].apply(
            lambda x: 'Sim' if isinstance(x, str) and x.strip()else'Não') 


        arquivo_final['Taxa de Gestão'] =arquivo_final['Taxa de Gestão'].fillna(0)
        arquivo_final['Taxa de Gestão'] = pd.to_numeric(arquivo_final['Taxa de Gestão'],errors='coerce')
        print(arquivo_final.info())
        arquivo_final['Taxa de Gestão'] = (arquivo_final['Taxa de Gestão']*100).map('{:.6f}'.format)
        arquivo_final['Rentabilidade'] = (arquivo_final['Rentabilidade']).fillna(0).map('{:.7f}'.format)

        duas_casa_decimais = ['Aportes', 'Retiradas', 'PL Total',  'Fundos']
        for colunas in duas_casa_decimais:
            arquivo_final[colunas] = arquivo_final[colunas].fillna(0).map('{:,.2f}'.format)

        def padrao_numerico_br(df,coluna):

                    df[coluna] = df[coluna].astype(str)
                    df[coluna] = df[coluna].str.replace('.','_')
                    df[coluna] = df[coluna].str.replace(',','.')    
                    df[coluna] = df[coluna].str.replace('_',',')
                    return df[coluna]


        colunas_trocar_separador = ['Rentabilidade','Taxa de Gestão','Aportes', 'Retiradas', 'PL Total',  'Fundos']
        for colunas in colunas_trocar_separador:
            arquivo_final[colunas] = padrao_numerico_br(arquivo_final,colunas)

        status_das_contas = {'Ativo':'Ativa','Inativo':'Inativa','Pode Operar':'Ativa','Encerrado':'Encerrada'}
        arquivo_final['Status'] = arquivo_final['Status'].replace(status_das_contas)

        return arquivo_final


    def colocando_cod_anbima_e_finalizando_ajustes(arquivo_final,caminho_do_arquivo_retorno,data_maxima,mes_de_analise):

        cod_anbima_ultimo_form_enviado = pd.read_excel(caminho_do_arquivo_retorno)

        cod_anbima_ultimo_form_enviado = cod_anbima_ultimo_form_enviado.iloc[:,[1,-2,-1]]
        cod_anbima_ultimo_form_enviado.loc[:574 , 'Campo de apoio'] = '00' + cod_anbima_ultimo_form_enviado.loc[:574, 'Campo de apoio'].astype(str)
        cod_anbima_ultimo_form_enviado['Campo de apoio'] = cod_anbima_ultimo_form_enviado['Campo de apoio'].astype(str)
        arquivo_final = arquivo_final.merge(cod_anbima_ultimo_form_enviado,left_on='Conta',right_on='Campo de apoio', how='outer')
        arquivo_final = arquivo_final.iloc[:,[41,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,
                                        16,17,18,19,20,21
                                        ,22,23,24,25,26,27,28,29,30,31,32,33,34,35
                                        ,36,37,38,39,40]]

        arquivo_final['Início da Gestão'] = pd.to_datetime(arquivo_final['Início da Gestão'])
        arquivo_final = arquivo_final[arquivo_final['Início da Gestão']< pd.to_datetime(data_maxima)]

        encontrando_contas_novas = (arquivo_final['Início da Gestão']>pd.to_datetime(mes_de_analise))&(arquivo_final['Status']=='Ativa')
        arquivo_final.loc[encontrando_contas_novas, 'Código ANBIMA'] = '0011223344'
        arquivo_final['Início da Gestão'] = pd.to_datetime(arquivo_final['Início da Gestão']).dt.strftime("%d/%m/%Y")
        removendo_encerradas = (arquivo_final['Status' ] == 'Encerrada')&(arquivo_final['Código ANBIMA'].isnull())
        removendo_inativas = (arquivo_final['Status' ] == 'Inativa')&(arquivo_final['Código ANBIMA'].isnull())
        arquivo_final = arquivo_final.drop(arquivo_final[removendo_encerradas].index)
        arquivo_final = arquivo_final.drop(arquivo_final[removendo_inativas].index)
        arquivo_final['Código ANBIMA'] = arquivo_final['Código ANBIMA'].astype(str).str[:-2].replace('00112233','')
        arquivo_final = arquivo_final.iloc[:,[0,2,3,4,5,6,7,8,9,10,11,12,13,14,15,
                                        16,17,18,19,20,21
                                        ,22,23,24,25,26,27,28,29,30,31,32,33,34,35
                                        ,36,37,38,39,1]]
        
        return arquivo_final

    def adicionando_contas_sem_dados(caminho_contas_antigas,arquivo_final ):

        xp_e_avulsas = pd.read_excel(caminho_contas_antigas)
        limpar_colunas = ['Data distrato','Tipo de cobranca da taxa de performance','Descricao da taxa de performance','Benchmark TX. Perf',]
        for colunas in limpar_colunas:    
            xp_e_avulsas[colunas] = xp_e_avulsas[colunas].replace(0,'')

        xp_e_avulsas['Codigo ANBIMA'] = xp_e_avulsas['Codigo ANBIMA'].astype(str)
        xp_e_avulsas = xp_e_avulsas.rename(columns={'Codigo ANBIMA':'Código ANBIMA'})

        arquivo_final = pd.concat([arquivo_final,xp_e_avulsas]).reset_index(drop=True) 
        arquivo_final['Início da Gestão'] = pd.to_datetime(arquivo_final['Início da Gestão']).dt.strftime("%d/%m/%Y")
        arquivo_final['Taxa de Gestão'] = arquivo_final['Taxa de Gestão'].replace('2,50000','2,500000')
        arquivo_final = arquivo_final.iloc[:,[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23
                                            ,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39]].rename(columns={'Conta':'ID'})
        arquivo_final['Código ANBIMA'] = arquivo_final['Código ANBIMA'].replace('n','')
        arquivo_final['Taxa de Gestão'] = arquivo_final['Taxa de Gestão'].replace('0,000000','0,000001')
        arquivo_final['Rentabilidade']=arquivo_final['Rentabilidade'].replace('-inf','0,00')
        arquivo_final['Benchmark TX. Perf'] = arquivo_final['Benchmark TX. Perf'].replace('S&P 500','OUTROS')
        
        arquivo_final['Descricao da taxa de performance'] = np.where(arquivo_final['Descricao da taxa de performance']=='10% do que exceder 100% do CDI','10% do que exceder CDI',arquivo_final['Descricao da taxa de performance']) 
        arquivo_final['Descricao da taxa de performance'] = np.where(arquivo_final['Descricao da taxa de performance']=='20% do que exceder 100% do CDI','20% do que exceder CDI',arquivo_final['Descricao da taxa de performance']) 
        arquivo_final['Descricao da taxa de performance'] = np.where(arquivo_final['Descricao da taxa de performance']=='20% do que exceder 100% do IFIX','20% do que exceder IFIX',arquivo_final['Descricao da taxa de performance']) 
        arquivo_final['Descricao da taxa de performance'] = np.where(arquivo_final['Descricao da taxa de performance']=='20% do que exceder 100% do IBOVESPA','20% do que exceder IBOVESPA',arquivo_final['Descricao da taxa de performance']) 
        arquivo_final['Descricao da taxa de performance'] = np.where(arquivo_final['Descricao da taxa de performance']=='20% do que exceder 100% do SMLL','20% do que exceder SMLL',arquivo_final['Descricao da taxa de performance']) 

                
        return arquivo_final


    def gerando_csv(arquivo_final):
        dia_hoje = datetime.now().strftime('%Y-%m-%d')
        arquivo_final.to_csv(f'ANBIMA___{dia_hoje}.csv',sep ='|', encoding='latin-1')

    def gerando_excel(arquivo_final):
        dia_hoje = datetime.now().strftime('%Y-%m-%d')
        arquivo_final.to_excel(f'EXCEL_Anbima{dia_hoje}.xlsx')


if __name__=="__main__":
    caminho_dados = Anbima_mensal(r'C:\Users\lauro.telles\Desktop\Relatorio ANBIMA-20231007T124445Z-001\ANBIMA') 

    #def btg(caminho_controle,caminho_base_clientes,caminho_rentabilidade):
    
    arquivo_btg = Anbima_mensal.btg(r'C:\Users\lauro.telles\Desktop\Relatorio ANBIMA-20231007T124445Z-001\ANBIMA\ANBIMA Dezembro\BTG\Controle de Contratos - Atualizado Janeiro de 2024.xlsx',
                   r'C:\Users\lauro.telles\Desktop\Relatorio ANBIMA-20231007T124445Z-001\ANBIMA\ANBIMA Dezembro\BTG\Base BTG.xlsx',
                   r'C:\Users\lauro.telles\Desktop\Relatorio ANBIMA-20231007T124445Z-001\ANBIMA\ANBIMA Dezembro\BTG\Rentabilidade.xlsx')
    #def guide(caminho_dos_arquivos_controle,caminho_dos_arquivos_patrimonio,caminho_dos_arquivos_fundos,caminho_dos_arquivos_mes_anterior,caminho_aportes_resg):
    
    arquivo_guide = Anbima_mensal.guide(r'C:\Users\lauro.telles\Desktop\Relatorio ANBIMA-20231007T124445Z-001\ANBIMA\ANBIMA Dezembro\GUIDE\Controle de Contratos - Atualizado Janeiro de 2024.xlsx',
                                        r'C:\Users\lauro.telles\Desktop\Relatorio ANBIMA-20231007T124445Z-001\ANBIMA\ANBIMA Dezembro\GUIDE\PL Dezembro.xlsx',
                                        r'C:\Users\lauro.telles\Desktop\Relatorio ANBIMA-20231007T124445Z-001\ANBIMA\ANBIMA Dezembro\GUIDE\PL Dezembro.xlsx',
                                        r'C:\Users\lauro.telles\Desktop\Relatorio ANBIMA-20231007T124445Z-001\ANBIMA\ANBIMA Dezembro\GUIDE\pl_fundos_novembro.xlsx',
                                        r'C:\Users\lauro.telles\Desktop\Relatorio ANBIMA-20231007T124445Z-001\ANBIMA\ANBIMA Dezembro\GUIDE\Aportes e resgates dezembro.xlsx')
    
    # def padronizando_dados(btg_final,guide_final,filtro_data):
    arquivo_final = Anbima_mensal.padronizando_dados(arquivo_btg,arquivo_guide,'2024-01-01')
    #def colocando_cod_anbima_e_finalizando_ajustes(self,arquivo_final,caminho_do_arquivo_retorno,data_maxima,mes_de_analise):
    arquivo_final = Anbima_mensal.colocando_cod_anbima_e_finalizando_ajustes(arquivo_final,
                                                                              r'C:\Users\lauro.telles\Desktop\Relatorio ANBIMA-20231007T124445Z-001\ANBIMA\Relatorio Abima SET2023\Retroativo Novembro\novembro_anbima_excel.xlsx',
                                                                              '2023-12-31','2023-12-01')
    #def adicionando_contas_sem_dados(caminho_contas_antigas,arquivo_final ):
    arquivo_final = Anbima_mensal.adicionando_contas_sem_dados(r'C:\Users\lauro.telles\Desktop\Relatorio ANBIMA-20231007T124445Z-001\ANBIMA\Arquivos Base\Arquivo com contas antigas xp e outras.xlsx',
                                                               arquivo_final)



    
