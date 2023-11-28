from flask import Flask, render_template
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)

@app.route('/')
def mostrar_informacoes():
    # Lê o arquivo CSV usando o Pandas
    url = "https://raw.githubusercontent.com/fivethirtyeight/data/master/alcohol-consumption/drinks.csv"
    dados = pd.read_csv(url)

    # Carrega os dados geográficos dos países
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    # Junta os dados geográficos com os dados do CSV
    merged = world.set_index('name').join(dados.set_index('country'))

    # Lista com os nomes das colunas de consumo para criar os mapas
    colunas_consumo = ['beer_servings', 'spirit_servings', 'wine_servings', 'total_litres_of_pure_alcohol']

    # Cria e salva os mapas para cada tipo de consumo
    imgs_encoded_mapas = []
    for coluna in colunas_consumo:
        # Plota o mapa-múndi com os países destacados
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        merged.plot(column=coluna, cmap='OrRd', linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)
        plt.title(f'{coluna.replace("_", " ").title()} por País')
        ax.axis('off')  # Remove os eixos do gráfico

        # Salva o mapa em formato de imagem
        img = BytesIO()
        plt.tight_layout()
        plt.savefig(img, format='png')
        img.seek(0)
        img_encoded_mapa = base64.b64encode(img.getvalue()).decode()
        imgs_encoded_mapas.append(img_encoded_mapa)

    # Cria e salva os gráficos para os 5 maiores valores de cada tipo de consumo
    imgs_encoded_graficos = []
    for coluna in colunas_consumo:
        top_consumo = dados.nlargest(5, coluna)
        
        # Plota o gráfico de barras com os 5 maiores valores
        plt.figure(figsize=(8, 6))
        top_consumo.plot(kind='bar', x='country', y=coluna, color='skyblue')
        plt.title(f'Top 5 Países com Maior {coluna.replace("_", " ").title()}')
        plt.xlabel('País')
        plt.ylabel(f'{coluna.replace("_", " ").title()}')
        plt.xticks(rotation=45, ha='right')  # Rotaciona os rótulos do eixo x

        # Salva o gráfico em formato de imagem
        img = BytesIO()
        plt.tight_layout()
        plt.savefig(img, format='png')
        img.seek(0)
        img_encoded_grafico = base64.b64encode(img.getvalue()).decode()
        imgs_encoded_graficos.append(img_encoded_grafico)

    # Retorna a página com as imagens dos mapas e gráficos embutidas no HTML
    html_content = "<h1>Consumo de Bebidas por País</h1>"
    html_content += f"<h1>--------------------------------------------------------------------------------------------------<h1/>"
    for idx, img_encoded_grafico in enumerate(imgs_encoded_graficos):
        html_content += f"<h2>Top 5 {colunas_consumo[idx].replace('_', ' ').title()}</h2>"
        html_content += f"<img src='data:image/png;base64,{img_encoded_grafico}'/>"
        html_content += f"<h1>--------------------------------------------------------------------------------------------------<h1/>"

    for idx, img_encoded_mapa in enumerate(imgs_encoded_mapas):
        html_content += f"<h2>{colunas_consumo[idx].replace('_', ' ').title()}</h2>"
        html_content += f"<img src='data:image/png;base64,{img_encoded_mapa}'/>"
        html_content += f"<h1>--------------------------------------------------------------------------------------------------<h1/>"

    return html_content

if __name__ == '__main__':
    app.run(debug=True)
