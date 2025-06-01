# vitivinicultura_flask_api/core.py
import requests
from bs4 import BeautifulSoup
import re
from utils import verify_option_value
 

links = [
    "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_02", # Produção
    "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_03", # Processamento
    "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_04", # Comercialização
    "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_05", # Importação
    "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_06", # Exportação
]

def extract_year(text):
    # Procurar um número entre colchetes usando regex
    # Exemplo de texto: Importação de espumantes [2024]
    if text:
        match = re.search(r"\[(\d{4})\]", text)
        if match:
            return match.group(1)  # Retorna o ano encontrado
        else:
            return None
    return None

def list_buttons_values(soup, class_name="btn_sopt"):
    """
    This function lists all buttons with the class 'btn_sopt' from the provided BeautifulSoup object.
    """
    buttons = soup.find_all("button", class_=class_name)
    for button in buttons:
        print(button.text)


def crawler_wine_prodution_data(url, option):
    """
    This function is a placeholder for the web crawler that will scrape wine production data.
    It currently returns a list of links to be crawled.
    """

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        wine_data = soup.find_all("button", class_="btn_sopt") 
        for wine in wine_data:
            print(wine.text)

    return True


def crawler_title_table(soup):
    div = soup.find('div', class_='content_center')
    
    if div:
        p_tag = div.find('p', class_='text_center')
        
        if p_tag:
            return p_tag.text.strip()
        else:
            return None
    else:
        return None


def crawler_header_table(wine_table):
    th_elements = wine_table.find_all('th') # encontrando o cabeçalho da tabela
                
    if th_elements:
        header_list = [th_element.text.strip() for th_element in th_elements]
        #current_tabel["header"] = header_list
    return header_list

def crawler_footer_table(soup,header_list):
    # Extrair o rodapé da tabela
    # Encontrar o elemento <tfoot> dentro da tabela
    tfoot = soup.find('tfoot', class_='tb_total')
    tfoot_data = None

    if tfoot:
        cells = tfoot.find_all('td')
        
        tfoot_data = {coluna: valor for coluna, valor in zip(header_list, [cell.text.strip() for cell in cells])}

    return tfoot_data

def extract_options_values_table(url):
    '''
    docstring:
    Esta função extrai os valores dos botões de opção da página analisada.
    Parameters:
    url (str): URL da página a ser analisada.
    Returns:
    list: lista de dicionários contendo os valores e textos dos botões de opção.
    '''
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find('table', class_='tb_base tb_header no_print')
    if table:   
        buttons = table.find_all('button', class_='btn_sopt')
        buttons_values = [ {"value": butt.get('value'), 
                            "text": butt.text.strip(), 
                            "active": butt.has_attr('id')}
            for butt in buttons  ]
        
        any_active_bu = any(item.get('id') == True for item in buttons_values)
        
        # Se nenhum item ativo, atribuir True ao primeiro item
        if not any_active_bu and buttons_values:
            buttons_values[0]['active'] = True

    return buttons_values

def crawler_rows_table(wine_table, header_list): 
    row_item_dict = {}
    row_list = []  

    rows = wine_table.find_all("tr")

    for row in rows:
        cells = row.find_all("td")

        if cells:
            if 'tb_item' in cells[0].get('class', []):
                row_item_dict = {}
                row_item_dict["item"] = {coluna: valor for coluna, valor in zip(header_list, [cell.text.strip() for cell in cells])}
                row_item_dict["subitens"] = []
                row_list.append(row_item_dict)

            elif 'tb_subitem' in cells[0].get('class', []):
                row_subitem_dict = {coluna: valor for coluna, valor in zip(header_list, [cell.text.strip() for cell in cells])}
                if "subitens" in row_item_dict:  # Garantir que subitens já está inicializado
                    row_item_dict["subitens"].append(row_subitem_dict)

            else:
                row_dict = {coluna: valor for coluna, valor in zip(header_list, [cell.text.strip() for cell in cells])}
                row_list.append(row_dict)
    return row_list

def crawler_wine_table(url, table_class=None, button_opt=None, input_year_value=None):

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Verifica se a URL contém o parâmetro de opção válido
        if button_opt:
            option_values = extract_options_values_table(url)
            is_option_value_valid = verify_option_value(option_values, "value", button_opt)
            if is_option_value_valid:
                url = url+f"&subopcao={button_opt}"
                response = requests.get(url)
                soup = BeautifulSoup(response.text, "html.parser")
            else:
                return {"Parâmetro inválido": f"O parâmetro de opção '{button_opt}' não é válido."}
        
        # Verifica se a URL contém o parâmetro de opção válido
        if input_year_value:
            soup = extract_interval_and_submit(url, input_year_value, button_opt)

        wine_table = None


        if table_class:
            wine_tables = soup.find_all("table", class_=table_class)
        else:
            wine_tables = soup.find_all("table")
        
        
        tables = []
        if wine_tables:
            header_list = []
            row_list = []

            for wine_table in wine_tables: 

                
                current_table = {}    
                current_table["url"] = url

                # Extrair o título da tabela
                title_text = crawler_title_table(soup)
                current_table["title"] = title_text
                # Extrair o ano da tabela
                year_table = extract_year(title_text)
                current_table["year"] = year_table

                # Encontrar o cabeçalho da tabela
                header_list = crawler_header_table(wine_table)
                current_table["header"] = header_list
                
                # Encontrar todas as linhas <tr> dentro da tabela                
                row_list = crawler_rows_table(wine_table, header_list)
                current_table["row_list"] = row_list

                # Encontrar o rodapé da tabela         
                tfoot_data = crawler_footer_table(soup,header_list)
                current_table["footer"] = tfoot_data
                
            tables.append(current_table)
    # print(current_table.get("title"),current_table.get("year"))
    return tables


def extract_interval_and_submit(url, year_to_submit, option=None):
    
    response = requests.get(url)
    response.encoding = 'utf-8' 

    soup = BeautifulSoup(response.text, 'html.parser')

    # Encontrar o texto do intervalo de anos
    label = soup.find('label', class_='lbl_pesq')
    if label:
        interval_text = label.text.strip()  # Extrair o texto do label
        print("Texto do intervalo:", interval_text)

        # Extrair os limites do intervalo de anos
        years = interval_text.split("[")[1].split("]")[0].split("-")  # [1970-2024]
        year_min, year_max = int(years[0]), int(years[1])

        print(f"Intervalo de anos disponível: {year_min}-{year_max}")

        # Verificar se o ano está dentro do intervalo que foi extraído da página
        if year_min <= year_to_submit <= year_max:
            print(f"O ano {year_to_submit} está dentro do intervalo permitido ({year_min}-{year_max}).")

            # Colocando os dados para submter o forms
            form_data = {
                "ano": year_to_submit
            }

            if option:
                form_data["subopcao"] = option

            # Fazer a submissão do formulário
            submit_response = requests.post(url, data=form_data)
            if submit_response.status_code == 200:
                print("Formulário submetido com sucesso!")
                soup = BeautifulSoup(submit_response.text, "html.parser")
                return soup
            
            else:
                print("Erro ao submeter o formulário:", submit_response.status_code)
                return None
        else:
            message = f"O ano {year_to_submit} está fora do intervalo permitido ({year_min}-{year_max})."
            print(message)
            return None # {"message": f"{message}"}
    else:
        print("Intervalo de anos não encontrado no HTML.")
    return None

if __name__ == "__main__":
    #(url, table_class=None, button_opt=None, input_year_value=None)
    r = crawler_wine_table(links[3],"tb_base tb_dados","subopt_03")
    print(r)