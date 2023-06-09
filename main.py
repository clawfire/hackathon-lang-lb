import os
import requests
import yt_dlp as youtube_dl
import csv
import openai


def call_openAI(csv_file="transcript.csv", language="EN", temperature=0.2):
    # Set up your OpenAI API credentials
    openai.api_key = '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'

    # Define the custom prompt to append
    prompt = f"""From the following CSV content :
- Translate the text in "Word List" column (written in luxembourgish) as a whole text to the "{language}" language, and make it more understandable. Use the entire text for context but put the translation of each sentence in the proper line
- Convert time code in the Start and End columns into dubbing time code.
- And finally generate a SRT content, by converting everything into srt file format

CSV content:"""

    # Extract the content from the CSV and append to prompt each line
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        for row in reader:
            prompt += ', '.join(row) + '\n'

    prompt+="""

    SRT content:
    """

    # Generate text using OpenAI GPT API
    print(f"🗣️ Interpreting in {language} using this prompt: ", prompt)
    response=openai.ChatCompletion.create(
        model='gpt-3.5-turbo-0301',
        messages=[{"content":prompt,"role":"user"}],
        temperature= temperature,
        max_tokens=1000 # Adjust the desired length of the output
    )

    # Extract the generated text
    print("✅ received response from openAI, using ", response.usage)
    output = response.choices[0].message.content.strip()

    # Save the output to a file
    output_file = f'transcript-{language}.srt'
    print("💾 Saving srt file")
    with open(output_file, 'w') as file:
        file.write(output)

    print(f"Your file for {language} is waiting for you here: ", output_file)


def convert_video_to_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        #'outtmpl': '%(title)s.%(ext)s',
        'outtmpl': 'audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        video_title = info.get('title', None)
        video_id = info.get('id', None)
        #audio_filename = f"{video_title}.mp3" if video_title else "audio.mp3"
        audio_filename = "audio.mp3"
        ydl.download([url])
    return audio_filename


def download_video(url):
    response = requests.get(url, stream=True)
    filename = url.split("/")[-1]
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return filename


def extract_audio_from_video(video_file):
    audio_filename = "audio.mp3"
    command = f"ffmpeg -i {video_file} -vn -ar 16000 -ac 1 -ab 192k -f mp3 {audio_filename}"
    os.system(command)
    return audio_filename


def send_audio_file(api_url, audio_file):
    headers = {
        'accept': 'application/json',
    }
    files = {
        'audio_file': ('audio.mp3', open(audio_file, 'rb'), 'audio/mpeg')
    }
    print("☎️ Sending file to the API [modem noise here]...")
    response = requests.post(api_url,headers=headers, files=files)
    print("✅ File send, text received")
    return response.json()

def extract_word_chunks(data, max_seconds=3):
    words = data['words']

    chunks = []
    current_chunk = {'start': None, 'end': None, 'word_list': []}

    for word in words:
        if current_chunk['start'] is None:
            current_chunk['start'] = word['startTime']

        if current_chunk['end'] is None or word['endTime'] - current_chunk['start'] <= max_seconds:
            current_chunk['end'] = word['endTime']
            current_chunk['word_list'].append(word['word'])
            current_chunk['word_list'].append(" ")
        else:
            chunks.append(current_chunk)
            current_chunk = {'start': word['startTime'], 'end': word['endTime'], 'word_list': [word['word']]}

    # Append the last chunk
    if current_chunk['start'] is not None:
        chunks.append(current_chunk)

    return chunks

def save_to_csv(chunks, csv_file="transcript.csv"):
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Start', 'End', 'Word List'])

        for chunk in chunks:
            writer.writerow([chunk['start'], chunk['end'], ''.join(chunk['word_list'])])




def main():
    conversion_type = input("Do you want to use a video or an audio file? (V/A): ")
    if conversion_type.lower() == 'v':
        url = input("🔗 Please paste the video URL : ")
        if 'youtube.com' in url:
            audio_file = convert_video_to_audio(url)
        else:
            video_file = download_video(url)
            audio_file = extract_audio_from_video(video_file)
    else:
        audio_file = input("🎵 Please paste the audio url: ")

    api_url = 'https://leonie.schreifmaschinn.lu/api/v1/listen'  # Remplacez par l'URL de votre API
    # Stop calling the API again and again :')
    if not os.path.exists("./transcript.csv"):
        response_json = send_audio_file(api_url, audio_file)
        print("✂️ cutting sentences into chunk of 3s of speach ...")
        chunks = extract_word_chunks(response_json);
        print("💾 Saving into csv file")
        save_to_csv(chunks)
    else:
        print("📄 Transcript detected, skipping API call to obtain it. Remove the file if you want a fresh one")
    # print(json.dumps(response_json, indent=4))
    print("☎️ Calling openAI API now. Please wait")
    call_openAI(language="EN")
    call_openAI(language="DE")
    call_openAI(language="FR")


if __name__ == "__main__":
    main()
