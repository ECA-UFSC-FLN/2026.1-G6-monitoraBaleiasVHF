import Analyser
import numpy as np
from rtlsdr import RtlSdr
import time
import matplotlib.pyplot as plt

VELOCIDADE_LUZ = 299792458.0

# ----------------------------------------------------------------------
# --- EXEMPLO DE USO PARA DETERMINAÇÃO DE ÂNGULO (DoA) ---
# ----------------------------------------------------------------------

# Frequencia do emissor: 434.041 MHz

# Criando os dados de teste
sample_rate = 2.048e6     # MS/s
freq_sinal = 101.300e6      # MHz
lambda_onda = VELOCIDADE_LUZ / freq_sinal
d_espacamento = lambda_onda / 2
print(f"Espaçamento desejado: {d_espacamento}")

analisador = Analyser.AnalisadorDoA(sample_rate, freq_sinal, d_espacamento)

sdr1 = RtlSdr(device_index=0)
# Configure SDR settings
sdr1.sample_rate = sample_rate  # 2.048 MS/s
sdr1.center_freq = freq_sinal  # 101.3 MHz
sdr1.gain = 'auto'
N_SAMPLES = 32 * 1024
N_FFT = 1024


sinal_A1 = sdr1.read_samples(N_SAMPLES)

plt.figure(figsize=(12, 8))

# Calcula a força total da onda (Magnitude)
amplitude = np.abs(sinal_A1[:500])

plt.subplot(2, 1, 1)
plt.plot(amplitude, color='green', label='Força do Sinal (Magnitude)')
plt.title("Sinal no Domínio do Tempo")
plt.xlabel("Amostras")
plt.ylabel("Amplitude")
plt.legend()
plt.grid(True)

# 2. Sinal no Domínio da Frequência (Espectro de Potência)
plt.subplot(2, 1, 2)
plt.psd(sinal_A1, NFFT=N_FFT, Fs=sample_rate/1e6, Fc=freq_sinal/1e6)
plt.title("Densidade Espectral de Potência (PSD)")
plt.xlabel("Frequência (MHz)")
plt.ylabel("Intensidade (dB/Hz)")

plt.tight_layout()
plt.show()

# Não esqueça de fechar o SDR ao finalizar
sdr1.close()    


sdr2 = RtlSdr(device_index=1)
# Configure SDR settings
sdr2.sample_rate = sample_rate  # 2.048 MS/s
sdr2.center_freq = freq_sinal  # 101.3 MHz
sdr2.gain = 'auto'
N_SAMPLES = 32 * 1024
N_FFT = 1024

# Cálculo com sinais lidos dos arquivos .iq
print("(!) Início da detecção:")
while True:
    sinal_A1 = sdr1.read_samples(N_SAMPLES)
    sinal_A2 = sdr2.read_samples(N_SAMPLES)
    angulo_estimado = analisador.calcular_doa(sinal_A1, sinal_A2)
    print(f"\n[Ângulo Estimado a partir dos Dados I/Q: {angulo_estimado:.2f}°]")
    time.sleep(0.1)
