import os
import pandas as pd
from app.controllers.sat_crawler_nf import Crawlers_SAT
from app.controllers.controller_app import Controller_APP
from config import SAT_USERNAME, SAT_PASSWORD, SAT_URL_QUERY, API_TOKEN_TWO_CAPTCHA
from config import BASE_URL, BASE_DOWNLOADS, BASE_FILES, BASE_DIR_EMPRESAS
from config import DATA_INICIO


list_type_process = [
    # [{"process": "nfe", "type": "E"}],
    # [{"process": "nfe", "type": "S"}],
    [{"process": "nfce", "type": "E"}],
    [{"process": "nfce", "type": "S"}],
]


# ---->> LIMPAR O DIRETÓRIO DE DOWNLOADS DE ARQUIVOS DO SAT PARA INICIAR NOVO CLICO DA AUTOMAÇÃO SEM GERAR CONFLITOS DE DUPLICATAS
for process in list_type_process:

    base_dir_files_temp = os.path.join(BASE_URL, BASE_DOWNLOADS)
    print(base_dir_files_temp)

    for arquivo in os.listdir(base_dir_files_temp):
        caminho_arquivo = os.path.join(base_dir_files_temp, arquivo)
        if os.path.isfile(caminho_arquivo) and os.path.splitext(arquivo)[1] == '.xlsx':
            os.remove(caminho_arquivo)
    

    # ---------------------------------------------------------------
    # ----->> RUN APP
    if process[0]["process"] == "nfe":
        file_dir_empresas = os.path.join(BASE_DIR_EMPRESAS, "empresas.xlsx")
    elif process[0]["process"] == "nfce":
        file_dir_empresas = os.path.join(BASE_DIR_EMPRESAS, "empresasnfce.xlsx")

    list_cnpj_query = list(pd.read_excel(file_dir_empresas)["CNPJ"].values)
    print(list_cnpj_query)
    APP = Crawlers_SAT(
        username=SAT_USERNAME,
        password=SAT_PASSWORD,
        APItoken_twoCaptcha=API_TOKEN_TWO_CAPTCHA,
        base_dir_files_temp=base_dir_files_temp)
    APP.query_nfe(
        data_inicio=DATA_INICIO,
        url_query_sat=SAT_URL_QUERY,
        type_query = process[0]["process"],
        type_process = process[0]["type"],
        list_identificadores = list_cnpj_query,
    )

   
    APP = Controller_APP(sat_username="", sat_password="")

    base_dir_files_temp_downloads = os.path.join(BASE_URL, BASE_DOWNLOADS)
    move_file_to_dir_nfe = os.path.join(BASE_URL, BASE_FILES)

    for arquivo in os.listdir(base_dir_files_temp_downloads):
        base_dir_files = os.path.join(base_dir_files_temp_downloads, arquivo)
        print(base_dir_files_temp_downloads)
        if os.path.isfile(base_dir_files) and os.path.splitext(arquivo)[1] == '.xlsx':
            print(base_dir_files)
            APP.get_file(
                type_query=process[0]["process"],
                type_process= process[0]["type"],
                path_file_dir=move_file_to_dir_nfe,
                file_dir=base_dir_files,
            )