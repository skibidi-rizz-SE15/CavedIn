import RPi.GPIO as GPIO
import time
from notes import *

# Define constants
BUZZER_PIN = 18

# Melody and durations arrays
melody = [
    NOTE_E5, NOTE_D5, NOTE_FS4, NOTE_GS4,
    NOTE_CS5, NOTE_B4, NOTE_D4, NOTE_E4,
    NOTE_B4, NOTE_A4, NOTE_CS4, NOTE_E4,
    NOTE_A4
]

durations = [
    8, 8, 4, 4,
    8, 8, 4, 4,
    8, 8, 4, 4,
    2
]

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUZZER_PIN, GPIO.OUT)

def play_tone(frequency, duration):
    if frequency > 0:
        period = 1.0 / frequency
        delay_time = period / 2
        end_time = time.time() + (duration / 1000.0)  # Convert duration to seconds

        while time.time() < end_time:
            GPIO.output(BUZZER_PIN, True)
            time.sleep(delay_time)
            GPIO.output(BUZZER_PIN, False)
            time.sleep(delay_time)
    else:
        time.sleep(duration / 1000.0)  # If frequency is 0 (rest), just wait

def loop():
    size = len(durations)
    for note, duration in zip(melody, durations):
        note_duration = 1000 / duration  # Duration in milliseconds
        play_tone(note, note_duration)

        # Pause between notes
        pause_between_notes = note_duration * 1.3
        time.sleep(pause_between_notes / 1000)  # Convert to seconds

def cleanup():
    GPIO.cleanup()

if __name__ == "__main__":
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()
