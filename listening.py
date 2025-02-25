import speech_recognition as sr
from astral import LocationInfo
from astral.sun import sun
from datetime import datetime, date
import pyttsx3
import requests
from googleapiclient.discovery import build
import vlc
import os
import time
import random
from pytube import YouTube
import threading
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
import logging
import threading
import newsapi
import json
from newsapi import NewsApiClient


logging.basicConfig(level=logging.DEBUG)

class Identification:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 195)
        self.engine.setProperty('volume', 1.0)  # Volume do resultado configurado para 100%
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'brazil' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break

    def verificar_horario(self):
        latitude = -23.5505
        longitude = -46.6333
        local = LocationInfo("São Paulo", "Brazil", "America/Sao_Paulo", latitude, longitude)

        solar_info = sun(local.observer, date=date.today(), tzinfo=local.timezone)

        hora_atual = datetime.now(local.timezone).time()

        if solar_info['sunrise'].time() <= hora_atual <= solar_info['sunset'].time():
            return "bom dia"
        else:
            return "boa noite"

    def falar(self, texto, volume=1.0):
        self.engine.setProperty('volume', volume)
        self.engine.say(texto)
        self.engine.runAndWait()

class Weather:
    @staticmethod
    def get_weather(latitude, longitude):
        url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true&timezone=America/Sao_Paulo"
        
        response = requests.get(url)
        data = response.json()
        
        if 'current_weather' in data:
            weather = data['current_weather']
            temperature = weather['temperature']
            windspeed = weather['windspeed']
            return f"A temperatura é {temperature} graus celsius com ventos de {windspeed} quilômetro por hora"
        else:
            return "Não consegui obter a previsão do tempo."

class YouTubePlayer:
    YOUTUBE_API_KEY = '*******************************************'
    player = None

    @staticmethod
    def search_and_play(query):
        youtube = build('youtube', 'v3', developerKey=YouTubePlayer.YOUTUBE_API_KEY)
        max_results = random.randint(1, 23)
        request = youtube.search().list(
            part="snippet",
            maxResults=max_results,
            q=query
        )
        response = request.execute()
        if response['items']:
            random_video = random.choice(response['items'])
            video_id = random_video['id']['videoId']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            threading.Thread(target=YouTubePlayer.play_video, args=(video_url,)).start()
            return f"Tocando {random_video['snippet']['title']}"
        else:
            return "Não encontrei o vídeo solicitado."

    @staticmethod
    def play_video(video_url):
        logging.debug(f"Playing video: {video_url}")
        yt = YouTube(video_url)
        
        stream = yt.streams.get_audio_only() 
        
        audio_file = 'temp_audio.mp4'
        stream.download(filename=audio_file)
        logging.debug(f"Downloaded audio to: {audio_file}")

        YouTubePlayer.player = vlc.MediaPlayer(audio_file)
        YouTubePlayer.player.audio_set_volume(50)  
        YouTubePlayer.player.play()
        logging.debug("Started VLC player")

        while YouTubePlayer.player.get_state() != vlc.State.Playing:
            time.sleep(0.1)

        logging.debug("VLC player is playing")

        while YouTubePlayer.player.get_state() != vlc.State.Ended:
            time.sleep(0.1)

        logging.debug("VLC player ended")

        YouTubePlayer.player.stop()
        os.remove(audio_file)
        logging.debug(f"Removed audio file: {audio_file}")


    @staticmethod
    def pause():
        if YouTubePlayer.player is not None:
            logging.debug("Pausing player")
            YouTubePlayer.player.pause()

    @staticmethod
    def resume():
        if YouTubePlayer.player is not None:
            logging.debug("Resuming player")
            YouTubePlayer.player.play()

    @staticmethod
    def stop():
        if YouTubePlayer.player is not None:
            logging.debug("Stopping player")
            YouTubePlayer.player.stop()
            audio_file = 'temp_audio.mp4'
            if os.path.exists(audio_file):
                os.remove(audio_file)
                logging.debug(f"Removed audio file: {audio_file}")

class RecognizeSpeech:

    @staticmethod
    def start_loop():
        engine = RecognizeSpeech.get_engine()
        if not RecognizeSpeech.loop_started:
            engine.startLoop(False)
            RecognizeSpeech.loop_started = True

    @staticmethod
    def reconhece_fala():
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Aguardando o comando 'Harry'...")
            audio = recognizer.listen(source)

        try:
            texto = recognizer.recognize_google(audio, language='pt-BR')
            print("Você disse: " + texto)
            return texto.lower()
        except sr.UnknownValueError:
            print("Não entendi o que foi dito")
            return None
        except sr.RequestError as e:
            print(f"Erro ao solicitar resultados; {e}")
            return None

    @staticmethod
    def responde_em_voz(texto, volume=1.0):  
        engine = pyttsx3.init()
        engine.setProperty('volume', volume)
        engine.say(texto)
        engine.runAndWait()

    @staticmethod
    def responde(texto):
        if texto is None:
            return
        
        if "harry oi" in texto:
            RecognizeSpeech.responde_em_voz("Oi! Como posso ajudar?", volume=1.0)

        elif "harry tudo bem" in texto or "harry como vai" in texto:
            RecognizeSpeech.responde_em_voz("Estou bem, obrigado por perguntar!", volume=2.0)

        elif "harry o que você é" in texto:
             RecognizeSpeech.responde_em_voz("Eu me chamo Harry, sou um assistente virtual em fase de estudos. Sendo assim, esta é a minha versão beta. Ainda vou passar por muitas melhorias e espero poder te ajudar sempre no futuro. Precisa de mais alguma coisa?", volume=1.0)

        elif "harry quem o criou" in texto:
            RecognizeSpeech.responde_em_voz("Eu fui criado por um jovem desenvolvedor chamado Thiago, mas também conhecido como Marteex.", volume=1.0)

        elif "harry horas" in texto or "harry quantas horas" in texto or "harry hora" in texto or "harry quantas horas são" in texto or "harry quantas horas sao" in texto:
            RecognizeSpeech.responde_em_voz("Agora são " + datetime.now().strftime("%H:%M"), volume=1.0)

        elif "qual é o sentido da vida" in texto or "qual sentido da vida" in texto or "qual e o sentido de viver" in texto or "qual é o sentido de viver" in texto:
            RecognizeSpeech.responde_em_voz("Essa é uma pergunta difícil! O sentido da vida é algo que cada pessoa precisa descobrir, geralmente demora anos ou até década. Meu desenvolvedor acredita que o sentido de viver e para que você mude o mundo, se ele não pensasse assim eu não existeria.")
            RecognizeSpeech.responde_em_voz("Mas, sinceramente, eu não sei. Eu sou apenas um assistente virtual, não tenho a mesma sabedoria de seres humanos")

        elif "harry clima" in texto or "harry temperatura" in texto:
            latitude = -23.5505  
            longitude = -46.6333  
            clima = Weather.get_weather(latitude, longitude)
            RecognizeSpeech.responde_em_voz(clima)

        elif "harry imite a alexa" in texto or "harry imite a google assistente" in texto or "harry imite alexia" in texto or "harry imitar a alexa" in texto or "harry imitar alexa" in texto or "harry imite o google assistente" in texto:
            RecognizeSpeech.responde_em_voz("Ok! Mimimimimimimimimimimimi... Eu sou inteligente. Olhe para mim! Eco.")

        elif "harry notícias de hoje" in texto or "harry me atulize" in texto or "harry atualizações" in texto or "harry notícias" in texto or "harry notícia" in texto:
            global parar_leitura
            parar_leitura = False
            news_api_key = '************************'
            news_url = f"https://newsapi.org/v2/top-headlines?country=br&apiKey={news_api_key}"

            response = requests.get(news_url)
            data = response.json()

            if data['status'] == 'ok' and data['totalResults'] > 0:
                news_text = "Aqui estão as principais notícias de hoje: "
                for article in data['articles']:
                    news_text += article['title'] + ". "
                RecognizeSpeech.responde_em_voz(news_text)
        
            
        elif "harry tocar" in texto or "tocar" in texto:
            query = texto.split("tocar")[1].strip()
            RecognizeSpeech.responde_com_musica(query)

        elif "harry pausar" in texto or "pausar" in texto or "pause" in texto or "harry house" in texto:
            YouTubePlayer.pause()

        elif "harry play" in texto:
            YouTubePlayer.resume()

        elif "harry stop" in texto or "harry parar" in texto:
            RecognizeSpeech.responde_em_voz("Parando de tocar a música", volume=1.0)
            YouTubePlayer.stop()

        elif "valor do bitcoin" in texto:
            cotacao = requests.get("https://economia.awesomeapi.com.br/json/all")
            cotacao_dic = cotacao.json()
            RecognizeSpeech.responde_em_voz("O valor do bit coin e de: {}".format(cotacao_dic['BTC']['bid']))

            

        else:
            RecognizeSpeech.responde_em_voz("Desculpe, não entendi o que você disse. Pode repetir?", volume=1.0)

    @staticmethod
    def responde_com_musica(query):
        threading.Thread(target=YouTubePlayer.search_and_play, args=(query,)).start()
        volume_anterior = pyttsx3.init().getProperty('volume')
        YouTubePlayer.search_and_play(query)
        pyttsx3.init().setProperty('volume', volume_anterior)

if __name__ == "__main__":
    while True:
        texto_reconhecido = RecognizeSpeech.reconhece_fala()
        if texto_reconhecido and "harry" in texto_reconhecido:
            Identification().falar("Sim, estou ouvindo...", volume=1.0)
            while True:
                comando = RecognizeSpeech.reconhece_fala()
                if comando == "harry sair":
                    Identification().falar("Encerrando o assistente. Até logo! Espero te ver mais vezes.", volume=1.0)
                    break
                RecognizeSpeech.responde(comando)
            break