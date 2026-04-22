import numpy as np
from rtlsdr import RtlSdr
import time
import matplotlib.pyplot as plt

VELOCIDADE_LUZ = 299792458.0

# ----------------------------------------------------------------------
# --- EXEMPLO DE USO PARA DETERMINAÇÃO DE ÂNGULO (DoA) ---
# ----------------------------------------------------------------------

# Frequencia do emissor: 434.041 MHz

import numpy as np
from scipy.signal import butter, lfilter

# --- Criação do Filtro Passa-Baixa para Dados Complexos ---
def aplicar_filtro_passa_baixa(sinal, sample_rate, corte_hz):
    """
    Aplica um filtro passa-baixa no sinal complexo.
    Para dados I/Q em banda base, um corte_hz de 200000 (200 kHz)
    vai manter as frequências de -200 kHz até +200 kHz.
    """
    nyq = 0.5 * sample_rate
    frequencia_corte_normalizada = corte_hz / nyq
    
    # Cria um filtro Butterworth passa-baixa de ordem 4
    b, a = butter(4, frequencia_corte_normalizada, btype='low')
    
    # Aplica o filtro no sinal complexo
    sinal_filtrado = lfilter(b, a, sinal)
    return sinal_filtrado



# Criando os dados de teste
sample_rate = 2.048e6     # MS/s
freq_sinal = 433.9     # MHz 434.041
lambda_onda = VELOCIDADE_LUZ / freq_sinal
d_espacamento = lambda_onda / 2
print(f"Espaçamento desejado: {d_espacamento}")

sdr1 = RtlSdr(device_index=0)
# Configure SDR settings
sdr1.sample_rate = sample_rate  # 2.048 MS/s
sdr1.center_freq = freq_sinal  # 101.3 MHz
sdr1.gain = 'auto'
N_SAMPLES = 32 * 1024
N_FFT = 1024

# --- Como usar no seu código ---
# Limite de +- 0.2 MHz = 200.000 Hz
limite_banda_hz = 50000  

# Aplica o filtro no sinal original
sinal_A1 = sdr1.read_samples(N_SAMPLES)
#sinal_A1_limpo = aplicar_filtro_passa_baixa(sinal_A1, sample_rate, limite_banda_hz)
sdr1.close()
print("Encerrado")

sdr1 = RtlSdr(device_index=0)
sdr1.sample_rate = sample_rate  # 2.048 MS/s
sdr1.center_freq = freq_sinal  # 101.3 MHz
sdr1.gain = 'auto'
sinal_A2 = sdr1.read_samples(N_SAMPLES)

sub = sinal_A1 - sinal_A2

plt.figure(figsize=(12, 8))

# Mostra a senoide
onda1 = np.real(sinal_A1[:100])

plt.subplot(2, 1, 1)
plt.plot(sub, color='green', label='Subtração')
plt.title("Sinal no Domínio do Tempo")
plt.xlabel("Amostras")
plt.ylabel("Amplitude")
plt.legend()
plt.grid(True)

plt.subplot(2, 1, 1)
plt.plot(sinal_A1, color='red', label='Com sinal')
plt.legend()

plt.subplot(2, 1, 1)
plt.plot(sinal_A2, color='blue', label='Sem sinal')
plt.legend()

# 2. Sinal no Domínio da Frequência (Espectro de Potência)
plt.subplot(2, 1, 2)
plt.psd(sub, NFFT=N_FFT, Fs=sample_rate/1e6, Fc=freq_sinal/1e6)  # Convertendo para MHz
plt.title("Densidade Espectral de Potência (PSD)")
plt.xlabel("Frequência (MHz)")
plt.ylabel("Intensidade (dB/Hz)")

# plt.subplot(2, 1, 2)
# plt.psd(sinal_A2, NFFT=N_FFT, Fs=sample_rate/1e6, Fc=freq_sinal/1e6)  # Convertendo para MHz

plt.tight_layout()
plt.show()

 



# sdr2 = RtlSdr(device_index=1)
# # Configure SDR settings
# sdr2.sample_rate = sample_rate  # 2.048 MS/s
# sdr2.center_freq = freq_sinal  # 101.3 MHz
# sdr2.gain = 'auto'
# N_SAMPLES = 32 * 1024
# N_FFT = 1024

# # Aplica o filtro no sinal original
# sinal_A2 = sdr2.read_samples(N_SAMPLES)
# sinal_A2_limpo = aplicar_filtro_passa_baixa(sinal_A2, sample_rate, limite_banda_hz)

# onda2 = np.real(sinal_A2[:500])

# plt.subplot(2, 1, 1)
# plt.plot(onda2, color='blue', label='Força do Sinal (Magnitude)')
# plt.title("Sinal no Domínio do Tempo")
# plt.xlabel("Amostras")
# plt.ylabel("Amplitude")
# plt.legend()
# plt.grid(True)

# plt.subplot(2, 1, 2)
# plt.psd(sinal_A2, NFFT=N_FFT, Fs=sample_rate/1e6, Fc=freq_sinal/1e6)  # Convertendo para MHz
# plt.title("Densidade Espectral de Potência (PSD)")
# plt.xlabel("Frequência (MHz)")
# plt.ylabel("Intensidade (dB/Hz)")
# plt.legend()

# plt.tight_layout()
# plt.show()

# # Cálculo com sinais lidos dos arquivos .iq
# # print("(!) Início da detecção:")
# # while True:
# #     sinal_A1 = sdr1.read_samples(N_SAMPLES)
# #     sinal_A2 = sdr2.read_samples(N_SAMPLES)
# #     angulo_estimado = analisador.calcular_doa(sinal_A1, sinal_A2)
# #     print(f"\n[Ângulo Estimado a partir dos Dados I/Q: {angulo_estimado:.2f}°]")
# #     time.sleep(0.1)
