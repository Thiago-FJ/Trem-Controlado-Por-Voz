import pyaudio  # Biblioteca para capturar áudio do microfone
import numpy as np  # Biblioteca para manipulação de arrays numéricos
import serial  # Biblioteca para comunicação via porta serial (Bluetooth)
import time  # Biblioteca para gerenciar tempos de espera


# Configuração do PyAudio para captura de áudio
CHUNK = 256  # Tamanho do buffer de áudio (menor valor = menor latência)
FORMAT = pyaudio.paInt16  # Formato do áudio (16 bits por amostra)
CHANNELS = 1  # Número de canais (1 = mono)
RATE = 44100  # Taxa de amostragem do áudio (44.1 kHz, padrão de CD)


# Configuração da comunicação Bluetooth
bluetooth_port = "COM6"  # Porta serial do módulo Bluetooth (ajuste conforme necessário)
baud_rate = 9600  # Taxa de transmissão de dados


# Tentativa de abrir a porta serial para comunicação com o Arduino
ser = None  # Variável para armazenar a conexão serial
try:
    ser = serial.Serial(bluetooth_port, baud_rate, timeout=1)  # Abre a porta serial com um tempo limite
    time.sleep(2)  # Aguarda 2 segundos para estabilizar a conexão
    print("✅ Bluetooth conectado com sucesso!")  # Mensagem de confirmação
except serial.SerialException as e:  # Se houver erro ao abrir a porta serial
    print(f"⚠ Erro ao abrir a porta serial: {e}")  # Exibe o erro no console
    exit()  # Encerra o programa


# Inicialização do PyAudio para capturar áudio do microfone
audio = pyaudio.PyAudio()


# Tentativa de abrir o fluxo de áudio
try:
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
except Exception as e:  # Caso haja erro ao acessar o microfone
    print(f"⚠ Erro ao acessar o microfone: {e}")
    exit()  # Encerra o programa


last_volume = -1  # Armazena o último valor enviado para evitar envios repetidos


def get_volume_level(data):
    """
    Calcula o nível de volume do áudio capturado.
    Usa a média quadrática (RMS) para calcular a intensidade do som.
    """
    try:
        # Converte os dados brutos de áudio para um array de inteiros de 16 bits
        audio_data = np.frombuffer(data, dtype=np.int16)
        
        if len(audio_data) == 0:  # Se não houver dados, retorna 0
            return 0


        # Calcula a intensidade RMS (Root Mean Square) do áudio
        rms = np.sqrt(np.mean(np.square(audio_data.astype(np.float32))))  
        
        # Normaliza o valor do volume para o intervalo de 0 a 100
        volume_level = min(100, int((2 * rms / (2**15)) * 200))
        
        return volume_level  # Retorna o nível de volume processado
    except Exception as e:
        print(f"⚠ Erro ao processar áudio: {e}")  # Mensagem de erro caso falhe
        return 0  # Retorna 0 em caso de erro


print("🎤 Monitorando áudio... Pressione Ctrl+C para parar.")  # Mensagem de início


# Loop principal para capturar o áudio continuamente e enviar os dados via Bluetooth
try:
    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)  # Captura um pedaço do áudio do microfone
        volume = get_volume_level(data)  # Calcula o nível de volume


        # Verifica se a porta serial está aberta e evita envios repetitivos
        if ser and ser.is_open and abs(volume - last_volume) > 2:  
            try:
                ser.write(f"{volume}\n".encode('utf-8'))  # Envia o valor via Bluetooth para o Arduino
                print(f"📤 Enviado: {volume}")  # Exibe o valor enviado no console
                last_volume = volume  # Atualiza o último valor enviado para evitar repetição
            except serial.SerialException as e:
                print(f"⚠ Erro ao enviar dados: {e}")  # Caso haja erro na transmissão dos dados


except KeyboardInterrupt:  # Captura a interrupção do usuário (Ctrl+C)
    print("\n⏹ Encerrando...")  # Mensagem de encerramento


finally:
    # Finaliza corretamente os recursos abertos
    stream.stop_stream()  # Para a captura de áudio
    stream.close()  # Fecha o fluxo de áudio
    audio.terminate()  # Finaliza a instância do PyAudio
    if ser:  # Se a conexão Bluetooth estiver aberta, fecha a porta
        ser.close()
    print("🔌 Conexão finalizada.")  # Mensagem final de encerramento
