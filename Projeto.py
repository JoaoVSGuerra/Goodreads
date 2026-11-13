#cabeçário necessário
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
df = pd.read_csv("books.csv")
plt.style.use("ggplot")
pd.set_option("display.max_columns", None)

def limpeza(df):
    """aplica a limpeza dos dados e retorna um dataframe limpo e um log"""
    #preparação da limpeza
    log = []
    n = len(df)
    df = df.copy()
    #padroniza o idioma,titulo e autor
    df["language_code"] = df["language_code"].fillna("desconhecido").str.strip().str.lower()
    df["title"] = df["title"].str.replace(r"\s+", " ", regex=True).str.strip()
    df["authors"] = df["authors"].str.replace(r"\s+", " ", regex=True).str.strip()
    #exclui as linhas cujas colunas apresentem valores importantes faltantes
    df = df.dropna(subset=[
    "original_publication_year",
    "average_rating",
    "ratings_count",
    "work_text_reviews_count"])
    #registra a quantidade de itens removidos nessa etapa
    log.append(("ausentes em colunas essenciais", n - len(df)))
    n = len(df)
    #elimina as linhas com id duplicado
    df = df.drop_duplicates(subset="id")
    #registra a quantidade de itens removidos nessa etapa
    log.append(("id duplicado", n - len(df)))
    n = len(df)
    #filtra e remove as linhas com notas invalidas, considerando o limite das notas, usando pandas
    df = df[
    (df["average_rating"] >= 1) &
    (df["average_rating"] <= 5)]
    #registra a quantidade de itens removidos nessa etapa
    log.append(("nota fora de 1 a 5", n - len(df)))
    n = len(df)
    #remoção de livros sem avaliação
    df = df[df["ratings_count"] > 0]
    #registra a quantidade de itens removidos nessa etapa
    log.append(("ratings_count <= 0", n - len(df)))   
    n = len(df)  
    #remoção de livros sem avaliação  
    df = df[df["work_text_reviews_count"] >= 0]
    #registra a quantidade de itens removidos nessa etapa
    log.append(("work_text_reviews_count < 0", n - len(df)))   
    n = len(df)  
    #converte o ano de publicação em inteiro
    df["original_publication_year"] = (
    df["original_publication_year"].astype(int))
    #cria um dicionario de equivalencia para transformar os languages code em idioma
    idiomas = {
    "eng": "Inglês",
    "en": "Inglês",
    "en-us": "Inglês",
    "en-gb": "Inglês",
    "en-ca": "Inglês",
    "ara": "Árabe",
    "dan": "Dinamarquês",
    "fil": "Filipino",
    "fre": "Francês",
    "ger": "Alemão",
    "ind": "Indonésio",
    "ita": "Italiano",
    "jpn": "Japonês",
    "mul": "Multilíngue",
    "nl": "Neerlandês",
    "nor": "Norueguês",
    "per": "Persa",
    "pol": "Polonês",
    "por": "Português",
    "rum": "Romeno",
    "rus": "Russo",
    "spa": "Espanhol",
    "swe": "Sueco",
    "tur": "Turco",
    "vie": "Vietnamita"}
    #troca os codigos pelo idioma
    df["language_code"] = df["language_code"].replace(idiomas)
    # Conta idiomas sem informação
    qtd_desconhecidos = (
    df["language_code"] == "desconhecido"
    ).sum()
    log.append(("idiomas não informados", qtd_desconhecidos))
    # Verifica códigos não reconhecidos
    nao_reconhecidos = set(df["language_code"]) - set(idiomas.values()) - {"desconhecido"}
    print("Códigos não reconhecidos:", nao_reconhecidos)
    #retorna o resultado da limpeza
    return df, log

print('Limpeza:')

df_limpo, relatorio = limpeza(df)
df_limpo.to_csv("books_limpos.csv", index=False)
for motivo, qtd in relatorio:
    print(f"{motivo}: {qtd}")

print("Livros finais:", len(df_limpo), "de", len(df))

print("-------------------------------------------------------------------------------")

print("Estatísticas descritivas")

#estatísticas descritivas
dt = pd.read_csv("books_limpos.csv")

def estatísticas(dados, colunas):
    """calcula as medidas descritivas das variaveis quantitativas e retorna um dataframe"""
    #calcula as medidas descritivas e o .T faz a transposição da tabela para apresentar as variaveis em linhas
    resumo = dados[colunas].describe().T
    #traduz os nomes das medidas
    resumo = resumo.rename(columns={
    "count": "n",
    "mean": "media",
    "std": "desvio_padrao",
    "min": "minimo",
    "25%": "q1",
    "50%": "mediana",
    "75%": "q3",
    "max": "maximo"})
    #calcula a diferença entre média e mediana
    resumo["dif_media_mediana"] = (
    resumo["media"] - resumo["mediana"])
    resumo["n"] = resumo["n"].astype(int)
    return resumo

variaveis = [
    "average_rating",
    "ratings_count",
    "work_text_reviews_count",
    "original_publication_year"
]

tabela_resumo = estatísticas(dt, variaveis)

print(tabela_resumo.round(2))
#exporta a tabela de estatística descritiva para um arquivo csv
tabela_resumo.round(2).to_csv(
    "resumo_numerico.csv")

print("------------------------------------------------------------------------------------------")

#tabela de frequência - idioma
def frequencia_idioma(dados, coluna):
    """calcula frequencias absolutas e relativas de uma variavel categórica e retorna um data frame"""
    # Conta as ocorrências de cada categoria
    frequencias = dados[coluna].value_counts(dropna=False)
    # Organiza os resultados em uma tabela
    tabela = frequencias.rename_axis("categoria").reset_index(name="n")
   # Calcula os percentuais
    tabela["percentual"] = (
       tabela["n"] / len(dados) * 100
   )

    return tabela
frequencia_idiomas = frequencia_idioma(
    dt,
    "language_code"
)

print(frequencia_idiomas.round(2))

print("------------------------------------------------------------------------------------------")

#tabela de frequencia - publicação
def frequencia_ano(dados, coluna):
    """calcula frequencias absolutas e relativas de uma variavel categórica e retorna um data frame"""
    #limita os grupos por ano de publicação
    limites = [-np.inf,1949,1999,np.inf]
    rotulos = ["Antes de 1950","1950-1999","2000 em diante"]
    #separa os livros em periodos
    periodos = pd.cut(dados[coluna],bins=limites,labels=rotulos)
    #conta os registros em cada período
    frequencias = periodos.value_counts( sort=False).reindex(rotulos, fill_value=0)
    #monta a tabela
    tabela = pd.DataFrame({"periodo": frequencias.index,"n": frequencias.values})
    tabela["percentual"] = (tabela["n"] / len(dados) * 100)
    return tabela

frequencia_periodos_livros = frequencia_ano(dt,"original_publication_year")
print(frequencia_periodos_livros.round(2))

#exporta os resultados para um arquivo csv
frequencia_idiomas.to_csv("frequencia_idiomas.csv",index=False,)
frequencia_periodos_livros.to_csv("frequencia_periodos.csv",index=False,)
