# MyDash

Esta é uma ferramenta que auxilia o cientista de dados a 
trabalhar seus dados nos processos de entendimento e limpeza
do dataset.

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

* Permitir salvar os dataset carregados para nao precisar subir novamente
* Permitir trabalhar em um dataset já salvo
* Permitir salvar o resultado de trabalho de um dataset 
* Permitir salvar os datasets como parquet
* Utilizar o https://github.com/vaexio/vaex para trabalhar com os dataframes maiores
* Permitir utilizar Dask?Swifter?Pandaralell?Vaex?


# Links

* https://www.datageeks.com.br/pre-processamento-de-dados/
* https://towardsdatascience.com/%EF%B8%8F-load-the-same-csv-file-10x-times-faster-and-with-10x-less-memory-%EF%B8%8F-e93b485086c7
* https://medium.com/swlh/6-ways-to-significantly-speed-up-pandas-with-a-couple-lines-of-code-part-2-7a9e41ba76dc 
* 

# Screens

![tela principal](https://github.com/berlotto/mydash/raw/main/screen.png)