# Video dubbing from lb to *

This project was made in 2 days during the '{lang: lb}' hackathon in 2023.

The goal of our proof of concept is to be able to do automated machine dubbing from video in Luxembourgish. The goal is to fasten the work of translators by providing a working base they can edit, but also fill the gap of lack of Luxembourgish support in automated video dubbing system.

This python programs let you:

1. Either download a video and extract audio track or use an already existing audio track
2. Convert the track to mono 16khz mp3 track
3. Run this track through schreifmaschinn's API (using Meta XLSR model) to get text extracted from speech
4. Group all words per ±3s (± 11 words considering human average speech speed is 220 wpm) in a CSV format `transcript.csv`
5. Send this, alongside a custom prompt, to chatGPT API in order to get it
   1. Translated in another language
   2. Rewrite to get a decent quality
   3. Split the translation back to the original timecode
   4. Change the timecode into dubbing timecode format
   5. Generate text following SRT template
6. Save the result, per language, in several `transcript-XX.srt`

You'll find a diagram of how it works, and you'll see in blue the already identified possible optimisation:

![working workflow diagram](/docs/automated_video_dubbing.svg)

## Prerequisites

- Python 3.x
- OpenAI Python package (`pip install openai`)
- YoutubeDL Python package (`pip install yt_dlp`)

## Usage

1. Clone the repository:

   ```bash
   git clone https://github.com/clawfire/hackathon-lang-lb
   ```

2. Navigate to the project directory:

    ```bash
    cd hackathon-lang-lb
    ```

3. Install the required packages:

    ```bash
    pip install openai
    pop install yt_dlp
    ```

4. Set up your OpenAI API key:

    - Sign up for an account at <https://platform.openai.com/>.
    - Retrieve your API key from the OpenAI dashboard.
    - Replace 'YOUR_API_KEY' with your actual API key in the csv_to_gpt_api.py file.

5. Run the python script

    ```bash
    python main.py
    ```

6. Check the output
    - The `lb` transcript can be found into `transcript.csv`
    - Each of the different languages srt can be fond in `transcript-[XX].srt`

## Customization

- Adjust the `max_tokens` parameter in the `main.py` file to control the length of the generated output.
- Adjust the destination language by duplicating the `call_openAI(language="EN")` lines and changing `EN` to any ISO-2 language

## Better results using GPT-4 model

We saw significative improvment regarding the quality of the translation and rewriting using chatGPT 4 model compared to GPT-3.5-turbo-0301. You'll find them, that you can use as benchmarks, into the </best_results> folder.

## Limitation of dubbing in Luxembourgish

So far, the schreifmaschinn's API is using a Meta XLSR model which returns dictionnay of words alongside their timestamp, and a very long text string, without sentences. We are using the power of chatGPT to translate and rewrite in several other languages and get pretty decent results (for automated systems) but rewriting in Luxembourg is, sadly, not great. Even using ChatGPT 4.0 model, the quality of the translation is very poor and cannot but used.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](LICENSE)
