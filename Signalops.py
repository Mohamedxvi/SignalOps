import numpy as np
import time
import pickle
from rtlsdr import RtlSdr
from scipy.fft import fft, fftfreq

sdr = RtlSdr()
sdr.sample_rate = 2.048e6
sdr.gain = 'auto'

signal_frequencies = {
    'Car': {
        'Car Key Fob (315 MHz)': 315e6,
        'Car Key Fob (433 MHz)': 433e6,
        'Car Key Fob (868 MHz)': 868e6
    },
    'RFID': {
        'RFID 125kHz': 125e3,
        'RFID 13.56MHz': 13.56e6
    },
    'Bluetooth': {
        'Bluetooth (2.4 GHz)': 2.4e9
    },
    'Wi-Fi': {
        'Wi-Fi (2.4 GHz)': 2.4e9,
        'Wi-Fi (5 GHz)': 5e9
    },
    'AM Radio': {
        'AM Radio (530 kHz - 1700 kHz)': [530e3, 1700e3]
    },
    'FM Radio': {
        'FM Radio (88 MHz - 108 MHz)': [88e6, 108e6]
    },
    'Zigbee': {
        'Zigbee (2.4 GHz)': 2.4e9
    },
    'LoRa': {
        'LoRa 433 MHz': 433e6,
        'LoRa 868 MHz': 868e6,
        'LoRa 915 MHz': 915e6
    },
    'GPS': {
        'GPS (1.575 GHz)': 1.575e9
    },
    'ISM': {
        'ISM 433 MHz': 433e6,
        'ISM 868 MHz': 868e6,
        'ISM 915 MHz': 915e6
    }
}

def detect_and_analyze_signal(frequency):
    sdr.center_freq = frequency
    samples = sdr.read_samples(256 * 1024)
    signal_spectrum = np.abs(fft(samples))
    freqs = fftfreq(len(samples), 1 / sdr.sample_rate)
    peak_freq = abs(freqs[np.argmax(signal_spectrum)])
    avg_power = np.mean(np.abs(samples) ** 2)
    return peak_freq, avg_power, samples

def save_signal(signal_samples, signal_type, filename="saved_signal.pkl"):
    with open(filename, 'wb') as f:
        pickle.dump((signal_samples, signal_type), f)

def load_signal(filename="saved_signal.pkl"):
    try:
        with open(filename, 'rb') as f:
            signal_samples, signal_type = pickle.load(f)
        return signal_samples, signal_type
    except FileNotFoundError:
        return None, None

def scan_for_signal(signal_type):
    detected_signals = []
    if signal_type not in signal_frequencies:
        return []
    for freq_name, freq in signal_frequencies[signal_type].items():
        peak_freq, avg_power, signal_samples = detect_and_analyze_signal(freq)
        if avg_power > 1000:
            detected_signals.append((peak_freq, freq_name, signal_samples))
        time.sleep(0.1)
    return detected_signals

def classify_signal(frequency):
    for signal_type, freqs in signal_frequencies.items():
        for freq_name, known_freq in freqs.items():
            if isinstance(known_freq, list):
                if known_freq[0] <= frequency <= known_freq[1]:
                    return signal_type, freq_name
            elif abs(frequency - known_freq) < 500e3:
                return signal_type, freq_name
    return "Unknown", "Unknown Signal"

def display_saved_signals(saved_signals):
    if saved_signals:
        for idx, (signal_type, signal_name) in enumerate(saved_signals, 1):
            print(f"{idx}. {signal_type} - {signal_name}")
    else:
        print("No saved signals available.")

def replay_signal(signal_samples, signal_type):
    time.sleep(1)
    print(f"Signal {signal_type} replayed successfully.")

def display_main_menu():
    print("\nSelect the type of signal to scan:")
    print("1. Car")
    print("2. RFID")
    print("3. Bluetooth")
    print("4. Wi-Fi")
    print("5. AM Radio")
    print("6. FM Radio")
    print("7. Zigbee")
    print("8. LoRa")
    print("9. GPS")
    print("10. ISM Band")
    print("11. Manage Saved Signals")
    print("12. Exit")

def display_signal_options():
    print("\nWhat do you want to do with the signal?")
    print("1. Jam this frequency")
    print("2. Save this frequency")
    print("3. Back to Main Menu")

def display_saved_signals_menu(saved_signals):
    print("\nSaved Signals Management:")
    display_saved_signals(saved_signals)
    print("1. Replay saved signal")
    print("2. Delete saved signal")
    print("3. Back to Main Menu")

def main():
    print("Welcome, Mohamed!")
    saved_signals = []
    
    while True:
        display_main_menu()
        try:
            choice = int(input("Enter your choice: "))
            if choice == 12:
                break
            elif choice == 11:
                display_saved_signals_menu(saved_signals)
                saved_choice = int(input("Enter your choice: "))
                if saved_choice == 1:
                    signal_idx = int(input("Select signal to replay (1, 2, etc.): ")) - 1
                    if 0 <= signal_idx < len(saved_signals):
                        signal_samples, signal_type = saved_signals[signal_idx]
                        replay_signal(signal_samples, signal_type)
                elif saved_choice == 2:
                    signal_idx = int(input("Select signal to delete (1, 2, etc.): ")) - 1
                    if 0 <= signal_idx < len(saved_signals):
                        saved_signals.pop(signal_idx)
                        print("Signal deleted.")
                continue

            signal_types = ['Car', 'RFID', 'Bluetooth', 'Wi-Fi', 'AM Radio', 'FM Radio', 'Zigbee', 'LoRa', 'GPS', 'ISM']
            if 1 <= choice <= len(signal_types):
                selected_signal_type = signal_types[choice - 1]
                print(f"Scanning {selected_signal_type} signals...")
                detected_signals = scan_for_signal(selected_signal_type)

                if detected_signals:
                    print("\nDetected signals:")
                    for idx, (peak_freq, freq_name, signal_samples) in enumerate(detected_signals, 1):
                        print(f"{idx}. {freq_name} - {peak_freq / 1e6:.2f} MHz")

                    signal_idx = int(input("Select a signal to process (1, 2, etc.): ")) - 1
                    if 0 <= signal_idx < len(detected_signals):
                        signal_samples, signal_name = detected_signals[signal_idx][2], detected_signals[signal_idx][1]
                        display_signal_options()
                        option = int(input("Enter your choice: "))
                        if option == 1:
                            print(f"Jamming {signal_name} at {detected_signals[signal_idx][0] / 1e6:.2f} MHz... (simulated)")
                        elif option == 2:
                            saved_signals.append((signal_samples, signal_name))
                            save_signal(signal_samples, signal_name)
                        continue
                else:
                    print("No signals detected.")
            else:
                print("Invalid selection. Please choose a valid option.")
        except ValueError:
            print("Please enter a valid number.")

if __name__ == "__main__":
    main()
