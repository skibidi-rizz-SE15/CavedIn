import RPi.GPIO as GPIO
import time
from notes import *

# Define constants
BUZZER_PIN = 18

# Melody and durations arrays
start_melody = [
    NOTE_C4, None,
    NOTE_G4, None, NOTE_AS4, NOTE_C5, NOTE_AS4, None, NOTE_F4, NOTE_DS4, None,
    NOTE_C4, None, NOTE_E4, None, NOTE_G4, NOTE_A4, NOTE_AS4, None,
]

melody = [
    NOTE_C5, None, NOTE_C5, None, NOTE_AS4, None, NOTE_A4, None,
    NOTE_AS4, None, NOTE_AS4, NOTE_C5, None, NOTE_AS4, NOTE_A4, None,
    None, NOTE_C5, None, NOTE_AS4, None, NOTE_A4, None, NOTE_AS4, None, NOTE_E5, None,

    NOTE_C5, None, NOTE_C5, None, NOTE_AS4, None, NOTE_A4, None,
    NOTE_AS4, None, NOTE_AS4, NOTE_C5, None, NOTE_AS4, NOTE_A4, None,
    None, NOTE_C5, None, NOTE_AS4, None, NOTE_A4, None, NOTE_AS4, None, NOTE_E4, None,
]

start_durations = [
    4, 8, 4, 8, 4, 8, 8, 16, 8, 8, 16,
    4, 8, 4, 8, 4, 4, 4,
]

durations = [
    8, 16, 8, 16, 8, 16, 8, 16,
    8, 16, 8, 8, 16, 8, 8, 16,
    4,
    8, 16, 8, 16, 8, 16, 8, 2, 8,
    2,

    8, 16, 8, 16, 8, 16, 8, 16,
    8, 16, 8, 8, 16, 8, 8, 16,
    4,
    8, 16, 8, 16, 8, 16, 8, 2, 8,
    2
]

pwm = None
def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUZZER_PIN, GPIO.OUT)
    pwm = GPIO.PWM(BUZZER_PIN, 10)
    

def play_tone(frequency, duration):
    if frequency:
        period = 1.0 / frequency
        delay_time = period / 2  # Half the period for high signal
        for _ in range(int(duration / period)):
            # pwm.ChangeDutyCycle(100)
            GPIO.output(BUZZER_PIN, True)
            time.sleep(delay_time)
            GPIO.output(BUZZER_PIN, False)
            # pwm.ChangeDutyCycle(0)
            time.sleep(delay_time)

def play_start_melody():
    for note, duration in zip(start_melody, start_durations):
        if duration != 0:
            note_duration = 0.85 / duration  # Reduce the duration factor to speed up
            play_tone(note, note_duration)

        # Pause between notes
        time.sleep(note_duration * 0.7)  # Adjust pause to be shorter

def loop():
    while True:  # This creates an infinite loop
        for note, duration in zip(melody, durations):
            if duration != 0:
                note_duration = 0.85 / duration  # Reduce the duration factor to speed up
                play_tone(note, note_duration)

            # Pause between notes
            time.sleep(note_duration * 0.7)  # Adjust pause to be shorter

def cleanup():
    GPIO.cleanup()

if __name__ == "__main__":
    setup()
    try:
        play_start_melody()  # Play the start melody once
        loop()               # Start looping the main melody
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()
