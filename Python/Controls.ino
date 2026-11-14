const int BUZZER_PIN = 8; // 5V Active Buzzer
const int LED_PIN = 9;    // 5mm LED + 220 ohm resistor
const int BUTTON_PIN = 2; // Tactile push button (INPUT_PULLUP)

// Timing rules from Slide 8
const unsigned long BASE_UNIT = 120;     // 1T = 120ms
const unsigned long DOT_THRESHOLD = 250; // <250ms = Dot, >=250ms = Dash
const unsigned long LETTER_GAP = 360;    // 3T = 360ms
const unsigned long WORD_GAP = 840;      // 7T = 840ms
const unsigned long DEBOUNCE_DELAY = 30; // 30ms debounce

int buttonState = HIGH;
int lastReading = HIGH;
unsigned long lastDebounceTime = 0;
unsigned long pressStart = 0;
unsigned long releaseStart = 0;

bool sentLetterGap = true;
bool sentWordGap = true;

String txQueue = "";
unsigned long timer = 0;
unsigned long duration = 0;
bool isBeeping = false;
bool isPausing = false;

void setup()
{
    pinMode(BUZZER_PIN, OUTPUT);
    pinMode(LED_PIN, OUTPUT);
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    Serial.begin(9600);
}

void loop()
{
    unsigned long now = millis();
    readButton(now);
    readSerial();
    playQueue(now);
}

void readButton(unsigned long now)
{
    int reading = digitalRead(BUTTON_PIN);
    if (reading != lastReading)
    {
        lastDebounceTime = now;
    }

    if ((now - lastDebounceTime) > DEBOUNCE_DELAY)
    {
        if (reading != buttonState)
        {
            buttonState = reading;

            if (buttonState == LOW)
            {
                pressStart = now;
                digitalWrite(BUZZER_PIN, HIGH);
                digitalWrite(LED_PIN, HIGH);
            }
            else
            {
                digitalWrite(BUZZER_PIN, LOW);
                digitalWrite(LED_PIN, LOW);
                releaseStart = now;

                if ((now - pressStart) < DOT_THRESHOLD)
                {
                    Serial.print('.');
                }
                else
                {
                    Serial.print('-');
                }
                sentLetterGap = false;
                sentWordGap = false;
            }
        }
    }
    lastReading = reading;

    if (buttonState == HIGH)
    {
        unsigned long silence = now - releaseStart;
        if (!sentLetterGap && silence >= LETTER_GAP)
        {
            Serial.print(' '); // Tells Python to decode the letter
            sentLetterGap = true;
        }
        if (sentLetterGap && !sentWordGap && silence >= WORD_GAP)
        {
            Serial.print('/'); // Tells Python to insert a word space
            sentWordGap = true;
        }
    }
}

void readSerial()
{
    while (Serial.available() > 0)
    {
        char c = Serial.read();
        if (c == '.' || c == '-' || c == ' ' || c == '/')
        {
            txQueue += c;
        }
    }
}

void playQueue(unsigned long now)
{
    if (isBeeping)
    {
        if (now - timer >= duration)
        {
            digitalWrite(BUZZER_PIN, LOW);
            digitalWrite(LED_PIN, LOW);
            isBeeping = false;
            isPausing = true;
            timer = now;
            duration = BASE_UNIT; // 120ms intra-character gap
        }
        return;
    }

    if (isPausing)
    {
        if (now - timer >= duration)
        {
            isPausing = false;
        }
        return;
    }

    if (txQueue.length() > 0)
    {
        char sym = txQueue.charAt(0);
        txQueue.remove(0, 1);

        if (sym == '.')
        {
            digitalWrite(BUZZER_PIN, HIGH);
            digitalWrite(LED_PIN, HIGH);
            isBeeping = true;
            timer = now;
            duration = BASE_UNIT; // 120ms
        }
        else if (sym == '-')
        {
            digitalWrite(BUZZER_PIN, HIGH);
            digitalWrite(LED_PIN, HIGH);
            isBeeping = true;
            timer = now;
            duration = BASE_UNIT * 3; // 360ms
        }
        else if (sym == ' ')
        {
            isPausing = true;
            timer = now;
            duration = LETTER_GAP - BASE_UNIT; // Total 360ms gap
        }
        else if (sym == '/')
        {
            isPausing = true;
            timer = now;
            duration = WORD_GAP - LETTER_GAP; // Total 840ms gap
        }
    }
}
