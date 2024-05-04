# import re
from io import BytesIO

import numpy as np
import pandas as pd
import requests
import streamlit as st

# from bs4 import BeautifulSoup
from PIL import Image
from wordcloud import ImageColorGenerator, WordCloud

CHARACTERS = ["Fry", "Bender", "Leela", "Zoidberg", "Farnsworth", "Zapp"]


# @st.cache(allow_output_mutation=True)
# def fetch_transcript_urls(base_url):
#     session = requests.Session()
#     response = session.get(base_url)
#     soup = BeautifulSoup(response.text, "html.parser")
#     transcript_links = []

#     for a in soup.find_all("a", href=True):
#         href = a["href"]
#         if "Transcript:" in href:
#             full_url = "https://theinfosphere.org" + href
#             transcript_links.append(full_url)

#     return transcript_links, session


# @st.cache
# def transcript_to_dataframe(url, session):
#     response = session.get(url)
#     soup = BeautifulSoup(response.text, "html.parser")
#     content = soup.get_text()
#     lines = content.split("\n")

#     dialogues = []
#     for line in lines:
#         line = line.replace("⨂", "")
#         cleaned_line = re.sub(r"\[.*?\]|\(\d{2}:\d{2}\)", "", line).strip()
#         if ":" in cleaned_line:
#             character, dialogue = cleaned_line.split(":", 1)
#             dialogues.append(
#                 {"character": character.strip(), "dialogue": dialogue.strip()}
#             )

#     return pd.DataFrame(dialogues, columns=["Line No.", "Dialogue"])


@st.cache_data
def generate_wordcloud(text: str, character: str) -> WordCloud:
    mask = np.array(Image.open(f"{character}.png"))
    mask[np.all(mask == [255, 255, 255, 255], axis=-1)] = [254, 254, 254, 255]
    mask[mask.sum(axis=2) == 0] = 255

    wc = WordCloud(
        background_color="black",
        max_words=1000,
        mask=mask,
        max_font_size=60,
        random_state=1,
        relative_scaling=0.75,
    ).generate(text)
    image_colors = ImageColorGenerator(mask)
    wc.recolor(color_func=image_colors)

    return wc


@st.cache_data
def get_character_dialogues() -> list[pd.DataFrame]:
    pickle_url = "https://github.com/TheDigitalGarbologist/BendersBigScore-WC/raw/main/character_dialogues.pkl"
    response = requests.get(pickle_url, timeout=10)
    response.raise_for_status()  # will raise an exception for 4xx/5xx errors
    return pd.read_pickle(BytesIO(response.content))


def main():
    # Choose a character
    character = st.selectbox("Select a character", CHARACTERS)

    # Generate wordcloud
    character_dialogues = get_character_dialogues()
    dialogues = character_dialogues[character]
    dialogue_text = " ".join(dialogues)
    wc = generate_wordcloud(dialogue_text, character)
    title = f"WC_{character}"
    st.image(wc.to_array(), caption=title, use_column_width=True)

    # Add a download button for the word cloud image
    buf = BytesIO()
    wc.to_image().save(buf, format="JPEG")
    image_bytes = buf.getvalue()
    st.download_button("Download Word Cloud", image_bytes, f"{title}.png")

    # Show the dialogue dataframe
    dialogues_df = pd.DataFrame(dialogues, columns=["Dialogue"])
    st.subheader("Lines of Dialogues")
    st.dataframe(dialogues_df)


if __name__ == "__main__":
    st.set_page_config(page_title="Futurama Word Clouds", page_icon="🚀")
    st.title("WELCOMEEEE to the Word Cloud Generator of Futurama!")
    st.markdown(
        """
        This Streamlit App pulls in the transcript of Futurama via https://theinfosphere.org, creates a subset of dataframes for each character, and converts the lines spoken by that character into a custom word cloud.
        """
    )

    main()
