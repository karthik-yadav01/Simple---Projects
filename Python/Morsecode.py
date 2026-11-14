import serial
import threading
import time

SERIAL_PORT = 'COM3'  
BAUD_RATE = 9600      

MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..',
    '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
    '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----',
    '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.',
    '!': '-.-.--', '/': '-..-.', '(': '-.--.', ')': '-.--.-',
    '&': '.-...', ':': '---...', ';': '-.-.-.', '=': '-...-',
    '+': '.-.-.', '-': '-....-', '_': '..--.-', '"': '.-..-.',
    '$': '...-..-', '@': '.--.-.'
}

REVERSE_MORSE_CODE_DICT = {
    morse: character for character, morse in MORSE_CODE_DICT.items()
}


def text_to_morse(text):
    morse_words = []
    for word in text.upper().split():
        morse_letters = []
        for character in word:
            if character not in MORSE_CODE_DICT:
                raise ValueError(f"Unsupported character: {character!r}")
            morse_letters.append(MORSE_CODE_DICT[character])
        morse_words.append(' '.join(morse_letters))
    return ' / '.join(morse_words)


def morse_to_text(morse):
    words = []
    for word in morse.strip().split('/'):
        letters = []
        for code in word.split():
            if code not in REVERSE_MORSE_CODE_DICT:
                raise ValueError(f"Unsupported Morse code: {code!r}")
            letters.append(REVERSE_MORSE_CODE_DICT[code])
        if letters:
            words.append(''.join(letters))
    return ' '.join(words)


def listen_from_arduino(ser):
    """Background thread that reads tapped Morse symbols and decodes them."""
    morse_buffer = ""
    while True:
        try:
            if ser.in_waiting > 0:
                char = ser.read(1).decode('utf-8', errors='ignore')
                
                if char in ['.', '-']:
                    morse_buffer += char
                elif char == ' ':
                    # 360ms letter gap received from Arduino
                    if morse_buffer:
                        try:
                            decoded = morse_to_text(morse_buffer)
                            print(decoded, end='', flush=True)
                        except ValueError:
                            print('?', end='', flush=True)
                        morse_buffer = ""
                elif char == '/':
                    # 840ms word gap received from Arduino
                    print(' ', end='', flush=True)
        except serial.SerialException:
            print("\n[Serial connection lost]")
            break
        time.sleep(0.01)


if __name__ == "__main__":
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
        time.sleep(2)  # Wait for Arduino auto-reset
    except serial.SerialException as e:
        print(f"Could not open {SERIAL_PORT}: {e}")
        exit(1)

    print("=== Full-Duplex Morse Code Telegraph ===")
    print("Type English and press Enter to beep/blink on Arduino.")
    print("Tap the physical button on Pin D2 to decode text here.\n")

    # Start background listener thread for full-duplex operation
    listener = threading.Thread(target=listen_from_arduino, args=(ser,), daemon=True)
    listener.start()

    try:
        while True:
            user_input = input()
            if user_input.strip().lower() == 'exit':
                break
            try:
                # Encode using your dictionary so punctuation works seamlessly
                morse_out = text_to_morse(user_input)
                print(f"[TX Morse]: {morse_out}")
                ser.write((morse_out + '\n').encode('utf-8'))
            except ValueError as error:
                print(f"[Translation error]: {error}")
    except KeyboardInterrupt:
        pass
    finally:
        ser.close()
        print("\nDisconnected.")
