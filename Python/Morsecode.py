
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


if __name__ == "__main__":
    print("Morse Code Translator")
    print("1. English to Morse")
    print("2. Morse to English")
    choice = input("Choose a direction (1 or 2): ").strip()
    user_input = input("Enter the message to translate: ")

    try:
        if choice == '1':
            translated_message = text_to_morse(user_input)
        elif choice == '2':
            translated_message = morse_to_text(user_input)
        else:
            raise ValueError("Choose 1 for English to Morse or 2 for Morse to English.")
        print("Translation:", translated_message)
    except ValueError as error:
        print("Translation error:", error)
