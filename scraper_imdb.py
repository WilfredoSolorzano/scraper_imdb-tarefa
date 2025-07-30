import requests
import time
import csv
import random
import concurrent.futures
from bs4 import BeautifulSoup
import os

# Cabeçalhos HTTP padrão
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
}

MAX_THREADS = 7

# Caminho para salvar em ~/Documentos/movies.csv
home_dir = os.path.expanduser("~")
CSV_FILE = os.path.join(home_dir, "Documentos", "movies.csv")

# Limpa e inicializa o arquivo CSV com cabeçalhos
def iniciar_csv():
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
        movie_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        movie_writer.writerow(['Título', 'Data', 'Nota', 'Sinopse'])

# Extrai os detalhes de um filme individual
def extract_movie_details(movie_link):
    time.sleep(random.uniform(0, 0.2))

    try:
        response = requests.get(movie_link, headers=headers)
        movie_soup = BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        print(f'Erro ao acessar {movie_link}: {e}')
        return

    if movie_soup is not None:
        title = date = rating = plot_text = None

        page_section = movie_soup.find('section', class_='ipc-page-section')
        if page_section:
            divs = page_section.find_all('div', recursive=False)
            if len(divs) > 1:
                target_div = divs[1]

                title_tag = target_div.find('h1')
                if title_tag:
                    title_span = title_tag.find('span')
                    if title_span:
                        title = title_span.get_text()

                date_tag = target_div.find('a', href=lambda href: href and 'releaseinfo' in href)
                if date_tag:
                    date = date_tag.get_text().strip()

        rating_tag = movie_soup.find('div', attrs={'data-testid': 'hero-rating-bar__aggregate-rating__score'})
        rating = rating_tag.get_text() if rating_tag else None

        plot_tag = movie_soup.find('span', attrs={'data-testid': 'plot-xs_to_m'})
        plot_text = plot_tag.get_text().strip() if plot_tag else None

        if all([title, date, rating, plot_text]):
            with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
                movie_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                movie_writer.writerow([title, date, rating, plot_text])
                print(f'✔ {title} adicionado com sucesso')

# Extrai links de filmes da página principal
def extract_movies(soup):
    try:
        movies_table = soup.find('div', attrs={'data-testid': 'chart-layout-main-column'}).find('ul')
        movies_table_rows = movies_table.find_all('li')
        movie_links = ['https://imdb.com' + movie.find('a')['href'] for movie in movies_table_rows [:7]]
    except Exception as e:
        print(f'Erro ao extrair links de filmes: {e}')
        return

    threads = min(MAX_THREADS, len(movie_links))
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(extract_movie_details, movie_links)

# Função principal
def main():
    iniciar_csv()
    start_time = time.time()

    print("🔍 Acessando página do IMDB...")
    url = 'https://www.imdb.com/chart/moviemeter/?ref_=nv_mv_mpm'
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        extract_movies(soup)
    except Exception as e:
        print(f'Erro ao acessar a página principal: {e}')
        return

    print(f'⏱ Tempo total: {round(time.time() - start_time, 2)} segundos')
    print(f'📄 Dados salvos em: {CSV_FILE}')

if __name__ == '__main__':
    main()
