from time import sleep
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.common import keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from twocaptcha import TwoCaptcha


class Crawlers_SAT:
    def __init__(self, username, password, APItoken_twoCaptcha, base_dir_files_temp):
        self.username = username
        self.password = password
        self.APItoken_twoCaptcha = APItoken_twoCaptcha
        self.base_dir_files_temp = base_dir_files_temp


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

    def resolve_captcha(self, url_captcha):
        print(f"\n >>> URL CAPTCHA | URL: {url_captcha}")
        try:
            solver = TwoCaptcha(self.APItoken_twoCaptcha)
            result_captcha = solver.normal(url_captcha)
            print(result_captcha)
            print(f"\n\n\n >>>> CAPTCHA: {result_captcha}")
            return result_captcha
        except Exception as e:
            print(f" ### ERROR RESOLVE CAPTCHA | ERROR: {e}")
            return None
        
    def query_nfe(self, url_query_sat, list_identificadores, data_inicio, type_query, type_process):
        print(f"---------- type_query: {type_query}")
        print(f"---------- type_process: {type_process}")
        periodos = self.prepare_periodo_consulta(data_inicio=data_inicio)
        _data_inicio = periodos["data_inicio"]
        _data_final = periodos["data_fim"]

        options = webdriver.ChromeOptions()

        options.add_experimental_option('prefs', {
            'download.default_directory': self.base_dir_files_temp,
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'safebrowsing.enabled': True
        })
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()

        driver.get(url_query_sat)
        sleep(2)
        # ---- usuário e senha ----
        driver.find_element(By.ID, "Body_pnlMain_tbxUsername").send_keys(self.username)
        driver.find_element(By.ID, "Body_pnlMain_tbxUserPassword").send_keys(self.password)
        sleep(0.5)
        driver.find_element(By.ID, "Body_pnlMain_btnLogin").click()
        sleep(2)

        if type_query == "nfe":
            x =  driver.find_element(By.XPATH, '//*[@id="Body_Main_Main_sepConsultaNfpe_selTipoDocumento"]')
            drop=Select(x)
            drop.select_by_visible_text("NF-e")
        
        elif type_query == "nfce":
            x =  driver.find_element(By.XPATH, '//*[@id="Body_Main_Main_sepConsultaNfpe_selTipoDocumento"]')
            drop=Select(x)
            drop.select_by_visible_text("NFC-e")

        # ---- emitente e destinatário ----
        field_identificador = None
        if type_process == "E":
            print(" >>>>>>>>> EMITENTE ")
            field_identificador = driver.find_element(By.ID, "Body_Main_Main_sepConsultaNfpe_ctl10_idnEmitente_MaskedField")
        elif type_process == "S":
            print(" >>>>>>>>> DESTINATARIO ")
            field_identificador = driver.find_element(By.ID, "Body_Main_Main_sepConsultaNfpe_ctl11_idnDestinatario_MaskedField")
        


        print(field_identificador)
        field_emissao_inicial = driver.find_element(By.ID ,"Body_Main_Main_sepConsultaNfpe_datDataInicial")
        field_emissao_final = driver.find_element(By.ID ,"Body_Main_Main_sepConsultaNfpe_datDataFinal")

        btn_search = driver.find_element(By.ID, 'Body_Main_Main_sepConsultaNfpe_btnBuscar')
        
        last_captcha_value = None
        content_captcha = None
        repeat_process_identifiers = list()
        list_completed_identifiers = list()

        for identificador in list_identificadores:
            if identificador not in list_completed_identifiers:
                print(f" ### PROCESSANDO {identificador} | type_process: {type_process} | type_query: {type_query}")
                # limpa os campos de identificador --> Emitente e Destinatário
                driver.execute_script('document.getElementById("Body_Main_Main_sepConsultaNfpe_ctl10_idnEmitente_MaskedField").value = "";')
                driver.execute_script('document.getElementById("Body_Main_Main_sepConsultaNfpe_ctl11_idnDestinatario_MaskedField").value = "";')
                field_identificador.send_keys(identificador)
                
                field_emissao_inicial.send_keys(_data_inicio)
                field_emissao_final.send_keys(_data_final)
                sleep(1)
                element_captcha = driver.find_element(By.ID, "Body_Main_Main_sepConsultaNfpe_ctl17").find_element(By.TAG_NAME, "img").get_attribute("src")
                try:
                    if last_captcha_value != element_captcha:
                        content_captcha = self.resolve_captcha(url_captcha=element_captcha)
                        print(f"\n\n >>>>>> NOVO CAPTCHA RESOLVIDO: {content_captcha}")

                        # << field_captcha >> Este campo deve ser mapeado aqui para evitar falhas ao preencher com novos captchas.
                        field_captcha = driver.find_element(By.XPATH, '//*[@id="Body_Main_Main_sepConsultaNfpe_ctl21"]/div/input')
                    
                    # este processo limpa o input do captcha resolvido e preenche novamente a cada consulta.
                    # é necessário para evitar qualquer conflito com o captcha anterior.
                    driver.find_element(By.ID, 'Body_Main_Main_sepConsultaNfpe_ctl21').find_element(By.CLASS_NAME, 'input-group').find_element(By.TAG_NAME, 'input').clear()
                    field_captcha.send_keys(content_captcha["code"])
                    # ----
                    # necessário para verificar se gerou novo captcha.
                    last_captcha_value = element_captcha
                    # ----
                    print(f" \n\n >>> DATA CAPTCHAS {last_captcha_value} | {element_captcha}")
                    if content_captcha is not None:
                        try:
                            btn_search.click()
                            sleep(4)

                            check_error = list()
                            try:
                                list_check_error = driver.find_element(By.ID, "__SatMessageBox").find_element(By.CLASS_NAME, "sat-vs-error").find_elements(By.TAG_NAME, "li")
                                for e in list_check_error:
                                    check_error.append(e.text)
                            except:
                                pass
                            print(f" \n\n\n\n\n -------------------- CHECK ERROR -------------------- ")
                            print(check_error)

                            rows_table = driver.find_elements(By.XPATH, '//*[@id="Body_Main_Main_grpResultado_gridView"]/tbody/tr')
                            tt_reigstros = len(rows_table)
                            print(f"\n\n TOTAL REGISTROS: {tt_reigstros} | {type(tt_reigstros)}")
                            
                            # faz o download apenas se retornar 1 ou mais registros para a consulta.
                            if int(tt_reigstros) >= 1:
                                driver.find_element(By.ID, 'Body_Main_Main_grpResultado_btn0').click()
                                sleep(2)
                          
                            list_completed_identifiers.append({
                                identificador: tt_reigstros,
                                "error": check_error,
                            })
                                
                            
                        except Exception as e:
                            print(f" \n\n\n >>>>>>>>>>>>>>>>>>>>>>>>>>> ERROR: {e}")
                            repeat_process_identifiers.append({
                                identificador: e,
                            })
                    else:
                        if identificador not in repeat_process_identifiers:
                            repeat_process_identifiers.append(identificador)
                
                except Exception as e:
                    print(f" ### ERROR PROCESS | ERROR: {e}")
                    if identificador not in repeat_process_identifiers:
                        repeat_process_identifiers.append({
                            identificador: e
                        })

            sleep(3)
        driver.close()

        print("\n\n --- CONCLUIDOS --- \n", list_completed_identifiers)
        for i in list_completed_identifiers:
            print(i)
        print("\n\n --- COM ERROS ---\n", repeat_process_identifiers)
        return