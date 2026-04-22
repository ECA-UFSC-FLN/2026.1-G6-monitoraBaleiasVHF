import numpy as np
import matplotlib.pyplot as plt
from rtlsdr import RtlSdr
from scipy.signal import butter, filtfilt

# -------------------------------
# CONFIGURAÇÕES
# -------------------------------
sample_rate = 2.048e6
freq_center = 433.9e6
N_SAMPLES = 32 * 1024
N_FFT = 1024

# -------------------------------
# FUNÇÕES
# -------------------------------

def aplicar_filtro_passa_baixa(sinal, sample_rate, corte_hz):
    nyq = 0.5 * sample_rate
    corte_norm = corte_hz / nyq
    b, a = butter(4, corte_norm, btype='low')
    return filtfilt(b, a, sinal)


def estimar_offset_freq_fft(sinal, sample_rate):
    fft = np.fft.fftshift(np.fft.fft(sinal))
    freqs = np.fft.fftshift(np.fft.fftfreq(len(sinal), 1/sample_rate))
    return freqs[np.argmax(np.abs(fft))]


def mixar_para_baseband(sinal, sample_rate, delta_f):
    t = np.arange(len(sinal)) / sample_rate
    return sinal * np.exp(-1j * 2 * np.pi * delta_f * t)


def estimar_offset_fino_por_fase(sinal, sample_rate):
    fase = np.unwrap(np.angle(sinal))
    x = np.arange(len(fase))
    
    coef = np.polyfit(x, fase, 1)
    slope = coef[0]
    
    # converte inclinação da fase em Hz
    freq_offset = slope * sample_rate / (2 * np.pi)
    return freq_offset


# -------------------------------
# LEITURA SDR
# -------------------------------
sdr = RtlSdr()
sdr.sample_rate = sample_rate
sdr.center_freq = freq_center
sdr.gain = 20

print("Capturando sinal...")
sinal = sdr.read_samples(N_SAMPLES)
sdr.close()
print("Captura finalizada.")

# -------------------------------
# PROCESSAMENTO
# -------------------------------

# 1. Estimativa inicial (FFT)
delta_f_fft = estimar_offset_freq_fft(sinal, sample_rate)
print(f"Offset FFT: {delta_f_fft:.2f} Hz")

# 2. Mixagem inicial
sinal_bb = mixar_para_baseband(sinal, sample_rate, delta_f_fft)

# 3. Refinamento fino pela fase
delta_f_fino = estimar_offset_fino_por_fase(sinal_bb, sample_rate)
print(f"Correção fina: {delta_f_fino:.2f} Hz")

# 4. Mixagem fina
sinal_bb = mixar_para_baseband(sinal_bb, sample_rate, delta_f_fino)

# 5. Filtro mais estreito
sinal_filtrado = aplicar_filtro_passa_baixa(sinal_bb, sample_rate, 2000)

# 6. Remover bordas (evita artefato)
sinal_filtrado = sinal_filtrado[1000:-1000]

# -------------------------------
# ANÁLISES
# -------------------------------
tempo_real = np.real(sinal_filtrado[:2000])
magnitude = np.abs(sinal_filtrado[:2000])
fase = np.unwrap(np.angle(sinal_filtrado[:2000]))

# -------------------------------
# PLOTS
# -------------------------------
plt.figure(figsize=(12, 10))

# 1. Parte real
plt.subplot(4, 1, 1)
plt.plot(tempo_real)
plt.title("Parte Real (Tempo)")
plt.grid(True)

# 2. Magnitude
plt.subplot(4, 1, 2)
plt.plot(magnitude)
plt.title("Magnitude")
plt.grid(True)

# 3. Fase
plt.subplot(4, 1, 3)
plt.plot(fase)
plt.title("Fase (Unwrapped)")
plt.grid(True)

# 4. PSD
plt.subplot(4, 1, 4)
plt.psd(sinal_filtrado, NFFT=N_FFT, Fs=sample_rate/1e6, Fc=freq_center/1e6)
plt.title("PSD do Sinal Filtrado")
plt.xlabel("Frequência (MHz)")
plt.ylabel("dB/Hz")

plt.tight_layout()
plt.show()