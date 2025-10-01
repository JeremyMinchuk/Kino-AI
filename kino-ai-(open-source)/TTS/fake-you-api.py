import os
import shutil
import asyncio
import json
from fakeyou import AsyncFakeYou


jsonFile = "kino-ai-(open-source)\TTS\prompts.json"


async def order_of_speakers():
    """
    Extracts and returns the order of speakers from the JSON file.

    Returns:
        list: A list of speakers in the order they appear in the conversations.
    """
    with open(jsonFile, "r") as f:
        data = json.load(f)

    # Flatten the list of speakers across all conversations
    speakers_sorted = [dialogue["speaker"] for conversation in data["conversation"] for dialogue in conversation["dialogue"]]

    return speakers_sorted
    

async def order_of_dialogue():
    """
    Extracts and returns the dialogue in the order they appear in the JSON file.

    Returns:
        list: A list of dialogue strings in the order they appear in the conversations.
    """
    with open(jsonFile, "r") as f:
        data = json.load(f)

    # Flatten the list of dialogue across all conversations
    dialogue_sorted = [dialogue["dialogue"] for conversation in data["conversation"] for dialogue in conversation["dialogue"]]

    return dialogue_sorted



async def generate_audio():
    # Initialize the AsyncFakeYou client with your credentials
    fy = AsyncFakeYou()

    # Authenticate with the FakeYou API
    await fy.login(username="username", password="password")

    # voice id examples
    voice_ids = {
        "Donald Trump": "weight_ppqs5038bvkm6wc29w0xfebzy",
        "Andrew Tate": "weight_8p7s8cgxx0mytghejq53d81rk",
        "Elon Musk": "weight_q5xbb54g2vmeeq2722zzfs897"
    }

    speakers = await order_of_speakers()
    dialogue = await order_of_dialogue()
    counter = 0

    # Load progress if it exists
    progress_file = "kino-ai-(open-source)\TTS\progress.json"
    if os.path.exists(progress_file):
        with open(progress_file, "r") as f:
            progress = json.load(f)
    else:
        progress = {}

    for i, y in zip(speakers, dialogue):
        counter += 1
        audio_file = f"line{counter}.wav"

        # Skip already processed lines
        if str(counter) in progress and progress[str(counter)] == "completed":
            print(f"Skipping line {counter}, already completed.")
            continue

        current_voice = voice_ids.get(i, None)
        current_punchLine = y

        while True:
            try:
                # Set a timeout for the TTS generation
                result = await asyncio.wait_for(fy.say(current_punchLine, current_voice), timeout=90)

                with open(audio_file, "wb") as f:
                    f.write(result.content)
                    print(f"Audio saved to {audio_file}")

                destination = os.path.join("wavFiles", audio_file)
                shutil.move(audio_file, destination)
                print(f"Audio moved to {destination}")

                # Mark progress as completed
                progress[str(counter)] = "completed"
                with open(progress_file, "w") as f:
                    json.dump(progress, f)

                break  # Exit the retry loop on success

            except Exception as e:
                print(f"Failed to generate line {counter}: {e}. Retrying...")
                await asyncio.sleep(10)  # Add a delay to avoid rate limiting

        # Add a delay between requests to avoid rate limiting
        await asyncio.sleep(10)
        


# Run the async function
if __name__ == "__main__":
    asyncio.run(generate_audio())

    # NOTICE HOW SPEAKERS EQUALS THE ORDER OF SPEAKERS FUNCTION 
    # speakers = asyncio.run(order_of_speakers())
    # print(speakers)

    # dialogue = asyncio.run(order_of_dialogue())
    # print(dialogue)