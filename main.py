 
 
 
import requests
import time

BOT_TOKEN = "7755314152:AAGL0av1LryHdgNbBFEGBlhLUxc9XgdvWvg"
CHANNEL_ID = "-1002329162775"

# URL da API do IPCA
IPCA_API_URL = "https://servicodados.ibge.gov.br/api/v3/agregados/1737/periodos/-1/variaveis/2265?localidades=N1[all]"
IGPM_API_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.189/dados?formato=json"

ultimo_indice_ipca = None
ultimo_indice_igpm = None

def buscar_ipca():
    """Coleta os dados do IPCA via API do IBGE."""
    global ultimo_indice_ipca
    print("🔎 Buscando IPCA...")
    try:
        response = requests.get(IPCA_API_URL)
        data = response.json()
        if not data or "resultados" not in data[0]:
            print("⚠️ IPCA não encontrado no JSON!")
            return None, None
        
        resultado = data[0]["resultados"][0]["series"][0]
        mes = list(resultado["serie"].keys())[0]  # Último período disponível
        valor = resultado["serie"][mes]
        
        print(f"✅ IPCA encontrado: {valor}% para {mes}")
        return mes, valor
    except Exception as e:
        print("Erro ao buscar IPCA:", e)
        return None, None

def buscar_igpm():
    """Coleta os dados do IGP-M via API do Banco Central."""
    global ultimo_indice_igpm
    print("🔎 Buscando IGP-M...")
    try:
        response = requests.get(IGPM_API_URL)
        data = response.json()
        if not data:
            print("⚠️ IGP-M não encontrado no JSON!")
            return None, None
        
        ultimo = data[-1]  # Último valor disponível
        data_igpm = ultimo["data"]
        valor_igpm = ultimo["valor"]
        
        print(f"✅ IGP-M encontrado: {valor_igpm} para {data_igpm}")
        return data_igpm, valor_igpm
    except Exception as e:
        print("Erro ao buscar IGP-M:", e)
        return None, None

def send_message(message):
    """Envia uma mensagem para o canal no Telegram."""
    print("📤 Enviando mensagem para o Telegram...")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def monitorar_indices():
    """Monitoramento contínuo do IPCA e IGP-M."""
    global ultimo_indice_ipca, ultimo_indice_igpm

    while True:
        print("🔄 Verificando atualizações...")

        # Verifica o IPCA
        mes_ipca, val_ipca = buscar_ipca()
        if mes_ipca and mes_ipca != ultimo_indice_ipca:
            ultimo_indice_ipca = mes_ipca
            send_message(f"📢 *Novo IPCA!* 📅 {mes_ipca} 📊 {val_ipca}%")

        # Verifica o IGP-M
        data_igpm, val_igpm = buscar_igpm()
        if data_igpm and data_igpm != ultimo_indice_igpm:
            ultimo_indice_igpm = data_igpm
            send_message(f"📢 *Novo IGP-M!* 📅 {data_igpm} 📊 {val_igpm}")

        print("⏳ Aguardando 1 minuto para próxima verificação...")
        time.sleep(10 * 60 * 60)  # Verifica a cada 10 horas  # Verifica a cada 1 minuto

if __name__ == "__main__":
    print("🔎 Monitorando IPCA e IGP-M...")
    monitorar_indices()