import openai
import os # for open , close and save file
import tkinter as tk
from tkinter import ttk
import numpy as np
import whisper
import pyaudio
import wave
import ssl
import numba
ssl._create_default_https_context = ssl._create_unverified_context


# add the voice library
import speech_recognition as sr


# Set up OpenAI API credentials
openai.api_key = "" #put you api key here

language_translations = {
    'English': {'text': 'Enter Text:', 'source_lang': 'I Speak:', 'target_lang': 'Translate To:', 'translate': 'Translate', 'swap': 'Swap'},
    'Spanish': {'text': 'Ingrese texto:', 'source_lang': 'Hablo:', 'target_lang': 'Traducir a:', 'translate': 'Traducir', 'swap': 'Intercambiar'},
    'Chinese': {'text': '输入文字:', 'source_lang': '我说的语言:', 'target_lang': '翻译成:', 'translate': '翻译', 'swap': '调换'},
    'French': {'text': 'Entrer le texte:', 'source_lang': 'Je parle:', 'target_lang': 'Traduire en:', 'translate': 'Traduire', 'swap': 'Échanger'},
    'German': {'text': 'Text eingeben:', 'source_lang': 'Ich spreche:', 'target_lang': 'Übersetzen nach:', 'translate': 'Übersetzen', 'swap': 'Tauschen'},
    'Japanese': {'text': 'テキストを入力:', 'source_lang': '私は話します:', 'target_lang': '翻訳先:', 'translate': '翻訳', 'swap': '交換'},
    'Russian': {'text': 'Введите текст:', 'source_lang': 'Я говорю:', 'target_lang': 'Перевести на:', 'translate': 'Перевести', 'swap': 'Поменять'},
    'Italian': {'text': 'Inserisci testo:', 'source_lang': 'Parlo:', 'target_lang': 'Tradurre in:', 'translate': 'Tradurre', 'swap': 'Scambiare'},
    'Portuguese': {'text': 'Digite o texto:', 'source_lang': 'Eu falo:', 'target_lang': 'Traduzir para:', 'translate': 'Traduzir', 'swap': 'Trocar'},
    'Hindi': {'text': 'पाठ डालें:', 'source_lang': 'मैं बोलता हूँ:', 'target_lang': 'अनुवाद करें:', 'translate': 'अनुवाद करना', 'swap': 'अदला बदली करें'},
}





def on_speech_to_text_click():
    # Recording parameters
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = "audio.wav"

    audio = pyaudio.PyAudio()

    log_output.insert(tk.END, "Recording...")

    # Start recording
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = []
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    log_output.insert(tk.END, "Recording complete!")

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save as WAV
    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    # Load P model
    model = whisper.load_model("base")

    # Transcribe the audio
    try:
       # make log-Mel spectrogram and move to the same device as the model
    

        # You may need to map the detected language code to a human-readable name
        # detected_language = language_mapping[detected_language] 

       # source_lang_input.set(detected_language)  # Set the source language input to the detected language


        result = model.transcribe(WAVE_OUTPUT_FILENAME)
        text = result["text"]
        text_input.insert(tk.END, text)
        log_output.insert(tk.END, "Transcription successful!\n")
    except Exception as e:
        print("Sorry, I didn't catch that. Error:", str(e))




def update_labels(language):
    text_label.config(text=language_translations[language]['text'])
    source_lang_label.config(text=language_translations[language]['source_lang'])
    target_lang_label.config(text=language_translations[language]['target_lang'])
    translate_button.config(text=language_translations[language]['translate'])
    swap_button.config(text=language_translations[language]['swap'])


def translate_text(text, source_language, target_language):
    prompt = f"Translate the following '{source_language}' text to '{target_language}': {text}"
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that translates text."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.5,
    )
    translation = res.choices[0].message.content.strip()
    return ' '.join([translation[i:i+29] for i in range(0, len(translation), 29)])

def on_translate_click():
    text = text_input.get("1.0", tk.END).strip()
    source_language = source_lang_input.get()
    target_language = target_lang_input.get()
    translated_text = translate_text(text, source_language, target_language)
    result_label.config(text=translated_text)
    app.update_idletasks()


def reset_fields():
    text_input.delete("1.0", tk.END) # Clear the text input field
    result_label.config(text="") # Clear the result label
    log_output.delete("1.0", tk.END) # Clear the text input field


def swap_languages():
    current_source = source_lang_input.get()
    current_target = target_lang_input.get()
    source_lang_input.set(current_target)
    target_lang_input.set(current_source)
    reset_fields()

def on_source_language_change(event):
    text_input.delete("1.0", tk.END) # Clear the text input field
    result_label.config(text="") # Clear the result label


def update_height(event):
    lines = int(text_input.index(tk.END).split('.')[0])
    new_height = min(max(lines, 5), 25)
    text_input.config(height=new_height)
    reset_fields()

app = tk.Tk()
app.title("Multilingual Translation Tool")
app.minsize(400, 200)

common_languages = ["English", "Spanish", "Chinese", "French", "German", "Japanese", "Russian", "Italian", "Portuguese", "Hindi"]

text_label = ttk.Label(app)
text_label.grid(column=0, row=0, columnspan=3)
text_input = tk.Text(app, wrap=tk.WORD, height=5)
text_input.grid(column=0, row=1, columnspan=3, sticky=(tk.W, tk.E), padx=(20, 20))


def update_height(event):
    lines = int(text_input.index(tk.END).split('.')[0])
    new_height = min(max(lines, 5), 25)
    text_input.config(height=new_height)
text_input.bind("<KeyRelease>", update_height)

source_lang_label = ttk.Label(app)
source_lang_label.grid(column=0, row=2)
source_lang_input = ttk.Combobox(app, values=common_languages)
source_lang_input.grid(column=1, row=2)
source_lang_input.bind("<<ComboboxSelected>>", lambda event: update_labels(source_lang_input.get()))

swap_button = ttk.Button(app, command=swap_languages)
swap_button.grid(column=2, row=2, padx=(0,20))

target_lang_label = ttk.Label(app)
target_lang_label.grid(column=0, row=4)
target_lang_input = ttk.Combobox(app, values=common_languages)
target_lang_input.grid(column=1, row=4)

translate_button = ttk.Button(app, command=on_translate_click)
translate_button.grid(column=1, row=5)

speech_to_text_button = ttk.Button(app, text="Speak", command=on_speech_to_text_click)
speech_to_text_button.grid(column=0, row=6) # Adjust the row and column as needed


blank_label = ttk.Label(app, text="")
blank_label.grid(column=1, row=6)

result_label = ttk.Label(app, text="", wraplength=200)
result_label.grid(column=0, row=7, columnspan=3,pady=(0,20))

log_label = ttk.Label(app, text="Log:")
log_label.grid(column=0, row=8)
log_output = tk.Text(app, wrap=tk.WORD, height=3)
log_output.grid(column=0, row=9, columnspan=3)



# Initialize labels with default language
update_labels('English')

app.grid_columnconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=1)
app.mainloop()