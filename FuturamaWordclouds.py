import streamlit as st
import pandas as pd
import os
import re
import requests
import numpy as np
from bs4 import BeautifulSoup
from collections import defaultdict
from PIL import Image
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt

CHARACTERS = ['Fry', 'Bender', 'Leela', 'Zoidberg', 'Farnsworth', 'Zapp']

@st.cache(allow_output_mutation=True)
def fetch_transcript_urls(base_url):
    session = requests.Session()
    response = session.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    transcript_links = []

    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'Transcript:' in href:
            full_url = 'https://theinfosphere.org' + href
            transcript_links.append(full_url)
    
    return transcript_links, session

@st.cache
def transcript_to_dataframe(url, session):
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    content = soup.get_text()
    lines = content.split('\n')
    
    dialogues = []
    for line in lines:
        line = line.replace('⨂', '')
        cleaned_line = re.sub(r"\[.*?\]|\(\d{2}:\d{2}\)", "", line).strip()
        if ':' in cleaned_line:
            character, dialogue = cleaned_line.split(':', 1)
            dialogues.append({'character': character.strip(), 'dialogue': dialogue.strip()})

    return pd.DataFrame(dialogues)

def generate_wordcloud(text, title, mask_path):
    mask = np.array(Image.open(mask_path))
    mask[np.all(mask == [255, 255, 255, 255], axis=-1)] = [254, 254, 254, 255]
    mask[mask.sum(axis=2) == 0] = 255

    wc = WordCloud(background_color="black", max_words=1000, mask=mask,
                   max_font_size=60, random_state=1, relative_scaling=0.75).generate(text)
    image_colors = ImageColorGenerator(mask)
    wc.recolor(color_func=image_colors)

    plt.figure(figsize=(10, 10))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.title(title)
    plt.show()

def main(base_url, character):
    pickle_path = 'character_dialogues.pkl'
    if os.path.exists(pickle_path):
        character_dialogues = pd.read_pickle(pickle_path)
    else:
        transcript_urls, session = fetch_transcript_urls(base_url)
        character_dialogues = defaultdict(list)

        for url in transcript_urls:
            df = transcript_to_dataframe(url, session)
            for char in CHARACTERS:
                character_dialogue = df[df['character'] == char]['dialogue'].tolist()
                character_dialogues[char].extend(character_dialogue)

        pd.to_pickle(character_dialogues, pickle_path)
    
    if character in character_dialogues:
        dialogues = character_dialogues[character]
        dialogue_text = ' '.join(dialogues)
        mask_url = f'https://github.com/TheDigitalGarbologist/BendersBigScore-WC/blob/main/{character}.png?raw=true'
        generate_wordcloud(dialogue_text, f'WC_{character}', mask_url)

if __name__ == "__main__":
    st.title("Character Word Cloud Generator")
    
    base_url = 'https://theinfosphere.org/Episode_Transcript_Listing'
    character = st.selectbox("Select a character", CHARACTERS)
    
    if st.button("Generate Word Cloud"):
        main(base_url, character)

