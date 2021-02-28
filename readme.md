# MyDash

Esta é uma ferramenta que auxilia o cientista de dados a 
trabalhar seus dados nos processos de entendimento e limpeza
do dataset.

Foi criado baseado no dash.plotly.com

## Como funciona

De forma geral, temos várias abas que identificam os passos a serem feitos no
dataset.

Por enquanto apenas 1 dataset por vez é trabalhado.

Cada uma dessas abas tem ferramentas que permitem agir sobre os dados, colunas e
linhas do dataset de forma facilitada.

A ordem das abas tende a seguir uma ordem de trabalho, desde a obtenção dos 
dados até a visualização dos resultados de forma gráfica.

### Aba Dados

Aqui é possível carregar

### Aba Colunas

Aqui é possível:

* Renomear colunas
* Converter o tipo de dados
* Descartar colunas
* Preencher dados faltantes

### Aba Informacoes

Aqui serão apresentados dados estatísticos e de contagem dos dados

* mininmos e máximos, médias, mediana, percentis, etc..
* boxplots
* minigraficos de contagens categoricas
* distribuição
* etc..

### Aba Informacoes

Aqui é possível ver informações mais detalhadas sobre os dados de cada coluna 
do dataframe

### Aba Filtro e Limpeza

Aqui é onde limpamos dados não desejados, filtramos mais, corrigimos dados, 
entre outras ações necessárias.
Assim definimos quais filtros e alterações de dados serão feitas antes da 
visualização.

### Aba Visualizaçao

Gráficos de barras, pizza, linha, coorelação, box, word_cloud, etc...

# Todo

* Quantidade de registros duplicados (https://stackoverflow.com/questions/35584085/how-to-count-duplicate-rows-in-pandas-dataframe)
* Permitir salvar os dataset carregados para nao precisar subir novamente
* Permitir trabalhar em um dataset já salvo
* Permitir salvar o resultado de trabalho de um dataset 
* Permitir salvar os datasets como parquet
* Utilizar o https://github.com/vaexio/vaex para trabalhar com os dataframes maiores
* Permitir utilizar Dask?Swifter?Pandaralell?Vaex?
* Criar uma aba para fazer tabelas dinâmicas ?

Infos:
add : amplitude, moda
histograma, simetria da distribuição



# Links

* https://www.datageeks.com.br/pre-processamento-de-dados/
* https://towardsdatascience.com/%EF%B8%8F-load-the-same-csv-file-10x-times-faster-and-with-10x-less-memory-%EF%B8%8F-e93b485086c7
* https://medium.com/swlh/6-ways-to-significantly-speed-up-pandas-with-a-couple-lines-of-code-part-2-7a9e41ba76dc 


# Run local

    mkvirtualenv mydash -p python3
    pip install -r requirements.txt
    python mydash.py 
        Dash is running on http://127.0.0.1:8050/

        * Serving Flask app "mydash" (lazy loading)
        * Environment: production
        WARNING: This is a development server. Do not use it in a production deployment.
        Use a production WSGI server instead.
        * Debug mode: on



# Screens

![tela principal](https://github.com/berlotto/mydash/raw/main/mydash.gif)


#### Possiveis Nomes:

- repandas
- 