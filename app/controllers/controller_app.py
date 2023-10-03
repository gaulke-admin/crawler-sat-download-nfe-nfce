import os
import pandas as pd
from openpyxl import load_workbook
from datetime import datetime, timedelta


class Controller_APP:
    def __init__(self, sat_username, sat_password):
        self.sat_username = sat_username
        self.sat_password = sat_password

    def prepare_periodo_consulta(self, data_inicio):
        _dt_inicio = data_inicio
        data_inicio = datetime.strptime(data_inicio, '%d/%m/%Y')
        data_final = data_inicio.replace(day=28) + timedelta(days=4)
        
        dict_mounth = {
            1: "jan", 2: "fev", 3: "mar", 4: "abr", 5: "mai", 6: "jun",
            7: "jul", 8: "ago", 9: "set", 10: "out", 11: "nov", 12: "dez",
        }
        mounth = None
        year = data_inicio.year
        _m = dict_mounth[data_inicio.month]
        for k, v in dict_mounth.items():
            if v == _m:
                mounth = f"{k}-{_m}"
        print(mounth, year)

        periodos = {
            "mounth": mounth,
            "year": year,
            "data_inicio": _dt_inicio,
            "data_fim": (data_final - timedelta(days=data_final.day)).strftime('%d/%m/%Y'),
        }
        return periodos

    def converter_to_string(self, data):
        return str(data)
    
    def get_file(self, file_dir, path_file_dir, type_query, type_process):

        
        file = pd.read_excel(
            file_dir,
            engine="openpyxl",
            dtype={
                "CnpjOuCpfDoEmitente": str,
                "CnpjDoEmitente": str,
                "CpfDoEmitente": str,
                "IeDoEmitente": str,
                "NomeEmitente": str,
                "UfEmitente": str,
                "CnpjOuCpfDoDestinatario": str,
                "CnpjDoDestinatario": str,
                "CpfDoDestinatario": str,
                "NomeEmitente": str,
                "NomeDestinatario": str,
            },
        )
        print(file)
        dict_mounth = {
            1: "jan", 2: "fev", 3: "mar", 4: "abr", 5: "mai", 6: "jun",
            7: "jul", 8: "ago", 9: "set", 10: "out", 11: "nov", 12: "dez",
        }
        periodoReferecia = file["PeriodoDeReferencia"].values[0].split("/")
        mes = f"{periodoReferecia[0]}-{dict_mounth[int(periodoReferecia[0])]}"
        ano = int(periodoReferecia[1])


        if type_process == "E":
            CnpjOuCpfDoEmitente = file["CnpjOuCpfDoEmitente"].values[0]
            NomeEmitente = file["NomeEmitente"].values[0]
        else:
            CnpjOuCpfDoEmitente = file["CnpjOuCpfDoDestinatario"].values[0]
            NomeEmitente = file["NomeDestinatario"].values[0]
        file = file[[
            "ModeloDocumento",
            "TipoDeOperacaoEntradaOuSaida",
            "Situacao",
            "ChaveAcesso",
            "DataEmissao",
            "CnpjOuCpfDoEmitente",
            "NomeEmitente",
            "UfEmitente",
            "CnpjOuCpfDoDestinatario",
            "IeDoDestinatario",
            "NomeDestinatario",
            "UfDestinatario",
            "SerieDocumento",
            "NumeroDocumento",
            "ValorTotalNota",
            "ValorTotalICMS",
            "ValorBaseCalculoICMS",
        ]]

        obj_replaced_names_cols = {
            "ModeloDocumento": "Mod",
            "TipoDeOperacaoEntradaOuSaida": "Op",
            "Situacao": "Situacao",
            "ChaveAcesso": "ChaveAcesso",
            "DataEmissao": "DataEmissao",
            "CnpjOuCpfDoEmitente": "CnpjEmit.",
            "NomeEmitente": "NomeEmitente",
            "UfEmitente": "UFEm",
            "CnpjOuCpfDoDestinatario": "CnpjDest.",
            "IeDoDestinatario": "IeDest.",
            "NomeDestinatario": "NomeDestinatario",
            "UfDestinatario": "UFDe",
            "SerieDocumento": "Serie",
            "NumeroDocumento": "NFE",
            "ValorTotalNota": "Valor Total",
            "ValorTotalICMS": "ICMS",
            "ValorBaseCalculoICMS":	"BC ICMS",
        }

        if len(CnpjOuCpfDoEmitente) == 14:
            name_file=f"{NomeEmitente} - {CnpjOuCpfDoEmitente[8:-2]}-{CnpjOuCpfDoEmitente[12:]}",
        else:
            name_file=f"{NomeEmitente} - {CnpjOuCpfDoEmitente}",
        
        file.rename(columns=obj_replaced_names_cols)
        f = file
        file.to_excel('data_temp.xlsx', engine="openpyxl", index=False)
        self.save_file_to_excel(
            dataframe= f,
            path_file_dir= path_file_dir,
            type_query= type_query,
            name_file= f"{name_file[0]} - {type_query.upper()} - {type_process}",
            mounth= mes,
            year= ano,
            type_process=type_process
        )
        return
    
    
    def save_file_to_excel(self, dataframe, path_file_dir, type_query, name_file, mounth, year, type_process):

        if os.path.isdir(os.path.join(path_file_dir, f'{year}\\{mounth}\\{type_query}')):
            print(f'A pasta "{year}" existe no diretório.')
        else:
            print(f'A pasta "{year}" não existe no diretório.')
            # Criar a pasta
            os.makedirs(os.path.join(path_file_dir, f'{year}\\{mounth}\\{type_query}'))
            print(f'A pasta "{year}" foi criada no diretório.')
        
        path_file_dir = os.path.join(path_file_dir, f'{year}\\{mounth}\\{type_query}\\{name_file}.xlsx')

        path_file_dir = path_file_dir.replace("\\", "\\\\")
        dataframe.to_excel(path_file_dir)