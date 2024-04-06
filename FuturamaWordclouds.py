import pandas as pd, os , re, requests, numpy as np
from bs4 import BeautifulSoup
from tqdm.auto import tqdm
from collections import defaultdict
from PIL import Image
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_gradient_magnitude

%matplotlib inline
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
    
    return transcript_links

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
    # Change pure white (RGBA) to off-white
    white = [255, 255, 255, 255]  # RGBA for white
    off_white = [254, 254, 254, 255]  # RGBA for off-white
    mask[np.all(mask == white, axis=-1)] = off_white

    mask[mask.sum(axis=2) == 0] = 255
    # edges = np.mean([gaussian_gradient_magnitude(mask[:, :, i] / 255., 2) for i in range(3)], axis=0)
    # mask[edges > .08] = 255

    wc = WordCloud(background_color="black", max_words=1000, mask=mask, max_font_size=60, random_state=1, relative_scaling=0.75).generate(text)
    
    # Apply the image colors to the words
    image_colors = ImageColorGenerator(mask)
    wc.recolor(color_func=image_colors)

    # Plot
    plt.figure(figsize=(100, 100))
    plt.imshow(wc, interpolation='bilinear')
    plt.show()

def main(base_url):
    pickle_path = 'character_dialogues.pkl'
    if os.path.exists(pickle_path):
        character_dialogues = pd.read_pickle(pickle_path)
    else:
        session = requests.Session()
        transcript_urls = fetch_transcript_urls(base_url)
        characters = ['Fry', 'Bender', 'Leela', 'Zoidberg', 'Farnsworth','Zapp']
        character_dialogues = defaultdict(list)

        for url in tqdm(transcript_urls, desc='Processing Transcripts'):
            df = transcript_to_dataframe(url, session)
            for character in characters:
                character_dialogue = df[df['character'] == character]['dialogue'].tolist()
                character_dialogues[character].extend(character_dialogue)

        pd.to_pickle(character_dialogues, pickle_path)

    for character, dialogues in character_dialogues.items():
        dialogue_text = ' '.join(dialogues)
        mask_path = f'{character}.png'
        generate_wordcloud(dialogue_text, f'WC_{character}', mask_path)
        # break

if __name__ == "__main__":
    base_url = 'https://theinfosphere.org/Episode_Transcript_Listing'
    main(base_url)
