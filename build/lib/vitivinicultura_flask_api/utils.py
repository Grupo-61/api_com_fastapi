
def verify_option_value(list_options, key, waited_value):
    '''
    docstring: Função para verificar se um valor específico existe em uma lista de dicionários.
    Parameters:
    list_options (list): Lista de dicionários a serem verificados.
    key (str): Chave a ser verificada em cada dicionário.
    waited_value (str): Valor esperado associado à chave.
    Returns:
    bool: True se o valor esperado for encontrado, False caso contrário.
    '''
    for item in list_options:
        
        if item.get(key) == waited_value:
            return True  
    return False  
