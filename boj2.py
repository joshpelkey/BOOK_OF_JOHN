import sys
import random
from openai import OpenAI
from slack_sdk.webhook import WebhookClient
from slack_sdk.errors import SlackApiError
import requests
import subprocess
import base64
from urlextract import URLExtract

import keys

# Define constants for better readability
HOME_DIR = keys.home_dir
IMG_PATH = keys.img_path
OPENAI_API_KEY = keys.openai_api_key

# Slack webhook URLs
SLACK_AI_KEY = keys.slack_ai_key
SLACK_DEV_KEY = keys.slack_dev_key

client = OpenAI(api_key=OPENAI_API_KEY)

# Content Styles
CONTENT_STYLES = {
    1: "Verses",
    2: "Psalm",
    3: "Proverbial Selections",
    4: "Parable",
    5: "Poetic Addendum",
    6: "John's Jests"
}

def get_webhook_client(is_dev_mode):
    """
    Returns the appropriate WebhookClient based on the development mode flag.

    Args:
        is_dev_mode (bool): True if in development mode, False otherwise.

    Returns:
        WebhookClient: The Slack WebhookClient instance.
    """
    if is_dev_mode:
        return WebhookClient(f"https://hooks.slack.com/services/{SLACK_DEV_KEY}")
    else:
        return WebhookClient(f"https://hooks.slack.com/services/{SLACK_AI_KEY}")

def get_gpt_prompt(content_style, theme, activity_data, bro_gpt_text, number_verses, starting_verse_number):
    """
    Generates the prompt for ChatGPT.

    Args:
        content_style (int): The selected content style (1-6).
        theme (str): The selected theme for the story.
        activity_data (dict): The chosen activity data.
        bro_gpt_text (str): Text related to the bro, if applicable.
        number_verses (int): The number of verses in the story.
        starting_verse_number (int): The starting verse number.

    Returns:
        str: The GPT prompt.
    """
    if content_style == 1:  # Book/Chapter
        return (
            f"You are the greatest storyteller in the world. Tell me a descriptive story about John. "
            f"John loves to drink and loves to gamble. Tell me about when John was "
            f"{activity_data['activity']}{bro_gpt_text} "
            f"with the theme of {theme}. "
            f"Make sure to incorporate a cocktail which should be in theme with the story, "
            f"but do not give the cocktail a name. "
            f"Use exactly {number_verses} sentences. "
            f"Number each sentence, starting with {starting_verse_number}. "
            f"Add a new line after each sentence. "
            f"For example, {starting_verse_number}: Your first sentence goes here.\n\n"
        )
    elif content_style == 2:  # Psalms (Song Lyrics)
        return (
            f"Write a song about John experiencing {theme} while {activity_data['activity']}{bro_gpt_text}. "
            f"Incorporate a cocktail inspired by the theme but do not give the cocktail a name. "
            f"Choose from a number of different music styles like heavy metal, rap, 80 pop, classic rock, or something fun."
            f"Use no more than 150 words."
        )
    elif content_style == 3:  # Proverbs (One-Sentence Examples)
        return (
            f"Give me 3 short, insightful proverbs about John's experiences with {theme} "
            f"while {activity_data['activity']}{bro_gpt_text}. "
            f"Each proverb should be a single, impactful sentence, in quotes. "
            f"Tie the proverbs together in a short story using a religious tone. "
            f"Do not number the sentences and put two new lines between each quote."
        )
    elif content_style == 4:  # Parables (Short Story with Moral)
        return (
            f"Tell me a short parable about John's experiences with {theme} while {activity_data['activity']}{bro_gpt_text}. "
            f"The parable should have a clear moral or lesson and be extremely formal. "
            f"Use no more than 150 words."
        )
    elif content_style == 5:  # Poem
        return (
            f"Write a poem about John experiencing {theme} while {activity_data['activity']}{bro_gpt_text}. "
            f"Incorporate a cocktail inspired by the theme but do not give the cocktail a name. "
            f"The poem should have a poetic and reflective tone. Pick a poet to emulate but do not tell me who."
            f"Use no more than 50 words."
        )
    elif content_style == 6:  # Quips/Jokes
        return (
            f"Tell me a dirty joke about John's experiences with {theme} "
            f"while {activity_data['activity']}{bro_gpt_text} in the style of stand up comedy. "
            f"Use no more than 150 words. Do not preface the joke, just tell it."
        )
    else:
        raise ValueError("Invalid content style. Please select a style between 1 and 6.")

def generate_gpt_story(prompt, content_style):
    """
    Generates a story using the OpenAI GPT API.

    Args:
        prompt (str): The prompt for ChatGPT.
        content_style (int): The selected content style (1-6).

    Returns:
        str: The generated story.
    """
    if content_style == 1:  # Book/Chapter
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are the most prolific story teller of all time. "
                                            "You always leave your readers astonished, bewildered, intrigued, or some other strong emotion."},
                {"role": "user", "content": prompt}
            ],
            temperature=1
        )
        return response.choices[0].message.content

    elif content_style == 2:  # Psalms (Song Lyrics)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a skilled poet and lyricist."},
                {"role": "user", "content": prompt}
            ],
            temperature=1  # Lower temperature for more structured output
        )
        return response.choices[0].message.content

    elif content_style == 3:  # Proverbs (One-Sentence Examples)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a wise sage who can craft insightful proverbs."},
                {"role": "user", "content": prompt}
            ],
            temperature=1
        )
        return response.choices[0].message.content

    elif content_style == 4:  # Parables (Short Story with Moral)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a master storyteller who can weave captivating parables."},
                {"role": "user", "content": prompt}
            ],
            temperature=1
        )
        return response.choices[0].message.content

    elif content_style == 5:  # Poem
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a skilled poet."},
                {"role": "user", "content": prompt}
            ],
            temperature=1
        )
        return response.choices[0].message.content

    elif content_style == 6:  # Quips/Jokes
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a witty comedian and a wise guy."},
                {"role": "user", "content": prompt}
            ],
            temperature=1
        )
        return "\n".join(response.choices[0].message.content.split("\n"))

    else:
        raise ValueError("Invalid content style.")

def generate_dalle_prompt(story, bro_dalle_text, content_style):
    """
    Generates a concise DALL-E prompt using GPT-4.

    Args:
        story (str): The generated story from GPT.
        bro_dalle_text (str): Text related to the bro for DALL-E, if applicable.
        content_style (int): The selected content style (1-6).

    Returns:
        str: The DALL-E prompt, or None if no image is to be generated.
    """

    if content_style in [1, 4]:  # Chronicles, Parables (more visual narratives)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert image prompt engineer. "
                                            "Your task is to create a concise and evocative DALL-E prompt "
                                            "based on the provided text, suitable for generating a high-quality image. "
                                            "Incorporate character descriptions where relevant."},
                {"role": "user", "content": f"Generate a DALL-E prompt, less than 100 words, for an image that visually represents: {story} {bro_dalle_text}"}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content

    elif content_style in [2, 5]:  # Psalms, Verses (more abstract, mood-based)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert image prompt engineer. "
                                            "Your task is to create a concise and evocative DALL-E prompt "
                                            "based on the provided text, suitable for generating an abstract or symbolic image."},
                {"role": "user", "content": f"Generate a DALL-E prompt, less than 100 words, for an image that visually represents the mood and themes of: {story} {bro_dalle_text}"}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content

    elif content_style == 3:  # Proverbs (focus on core message)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert image prompt engineer. "
                                            "Your task is to create a concise and evocative DALL-E prompt "
                                            "that visually represents the core message of the proverb."},
                {"role": "user", "content": f"Generate a DALL-E prompt, less than 100 words, for an image that illustrates: {story} {bro_dalle_text}"}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content

    elif content_style == 6:  # Jests (humor and exaggeration)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert image prompt engineer. "
                                            "Your task is to create a concise and evocative DALL-E prompt "
                                            "that humorously illustrates the core idea of the joke. "
                                            "Incorporate character descriptions where relevant."},
                {"role": "user", "content": f"Generate a DALL-E prompt, less than 100 words, for a humorous image based on: {story} {bro_dalle_text}"}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content

    else:
        raise ValueError("Invalid content style.")

def generate_image(prompt, bro):
    """
    Generates an image using the OpenAI create edit API.
    Args:
        prompt (str): The prompt for the image model.

    Returns:
        str: The URL of the generated image, or None if no image is generated.
    """
    if prompt is None:
        return None  # No prompt, no image

    prompt_text = (
            f"The reference images provided are fictional character illustrations, each labeled by name. "
            f"Using the appropriate fictional character as artistic inspiration, "
            f"generate a new stylized and imaginative scene based on the following description: {prompt}. "
            f"The result should be creative, illustrative, and not intended to represent any real person. "
    )

    file1 = IMG_PATH + "John.png"

    if bro:
        name = bro['name']
        file2 = IMG_PATH + name +".png"

        response = client.images.edit(
                model="gpt-image-1",
                image=[
                    open(file1, "rb"),
                    open(file2, "rb"),
                    ],
                prompt=prompt_text,
                n=1,
                size="1024x1024",
        )
    else:
    
        response = client.images.edit(
                model="gpt-image-1",
                image=[
                    open(file1, "rb"),
                    ],
                prompt=prompt_text,
                n=1,
                size="1024x1024",

        )

    image_base64 = response.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)

    # Save the image to a file
    with open("boj.png", "wb") as f:
        f.write(image_bytes)

def generate_cocktail_recipe(theme, activity_data):
    """
    Generates a cocktail recipe using the OpenAI GPT API.

    Args:
        theme (str): The selected theme for the story.
        activity_data (dict): The chosen activity data.

    Returns:
        str: The generated cocktail recipe in markdown format, or None if no recipe is generated.
    """
    # Generate a recipe for these themes
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a mixologist. You mix up the most incredible cocktails."},
            {"role": "user", "content": f"Craft a cocktail recipe inspired by the theme of {theme} "
                                        f"and the activity of {activity_data['activity']}. "
                                        f"Give the cocktail a name and present the output as you find in a recipe book. "
                                        f"Only provide the drink name, recipe, and instructions. "
                                        f"Do not provide any links. "
                                        f"Provide the output in markdown formatting."},
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content

def upload_image_to_imgur():
    """
    Uploads the generated image to Imgur.

    Args:
        image_url (str): The URL of the image.

    Returns:
        str: The URL of the uploaded image on Imgur.
    """
    imgur_result = subprocess.run(
        [HOME_DIR + "/.local/bin/imgur-uploader", "boj.png"],
        stdout=subprocess.PIPE,
    )

    extractor = URLExtract()
    imgur_str = str(imgur_result)
    urls = extractor.find_urls(imgur_str)
    return urls[0][:-4]  # Remove trailing newline character

def send_slack_message(webhook_client, story, theme, activity_data, image_url, cocktail_recipe, content_style, str_numbers):
    """
    Sends the generated story, image, and recipe to Slack.

    Args:
        webhook_client (WebhookClient): The Slack WebhookClient instance.
        story (str): The generated story.
        theme (str): The selected theme for the story.
        activity_data (dict): The chosen activity data.
        image_url (str): The URL of the uploaded image.
        cocktail_recipe (str): The generated cocktail recipe.
        content_style (int): The selected content style.
    """
    try:
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": ":game_die: :beer: :game_die:  The Books of John  :game_die: :beer: :game_die:",
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "text": f"Book of {theme.capitalize()} | Chapter "
                                f"{activity_data['chapter_number']}: "
                                f"{activity_data['chapter_title']} | "
                                f"{CONTENT_STYLES[content_style]} "
                                f"{str_numbers}",
                        "type": "mrkdwn",
                    }
                ],
            },
            {"type": "divider"},
        ]

        if content_style == 1:  # Book/Chapter
            blocks.extend([
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": story},
                },
                {"type": "divider"},
            ])
        elif content_style == 2:  # Psalms (Song Lyrics)
            blocks.extend([
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": story},  # Format as lyrics
                },
                {"type": "divider"},
            ])
        elif content_style == 3:  # Proverbs (One-Sentence Examples)
            blocks.extend([
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": story},  # Use bullet points
                },
                {"type": "divider"},
            ])
        elif content_style == 4:  # Parables (Short Story with Moral)
            blocks.extend([
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": story},
                },
                {"type": "divider"},
            ])
        elif content_style == 5:  # Poem
            blocks.extend([
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": story},  # Use code block for better formatting
                },
                {"type": "divider"},
            ])
        elif content_style == 6:  # Quips/Jokes
            blocks.extend([
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": story},  # Use bullet points
                },
                {"type": "divider"},
            ])

        if image_url:
            blocks.extend([
                {
                    "type": "image",
                    "title": {
                        "type": "plain_text",
                        "text": f"[{theme.capitalize()} - Chapter "
                                f"{activity_data['chapter_number']}: "
                                f"{activity_data['chapter_title']}]",
                        "emoji": True,
                    },
                    "image_url": image_url,
                    "alt_text": dalle_prompt,
                },
                {"type": "divider"},
            ])

        if cocktail_recipe:
            blocks.extend([
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": cocktail_recipe},
                },
            ])

        if content_style == 1:
            intro_text="A daily reading from THE BOOKS OF JOHN...",
        elif content_style == 2:
            intro_text = "A new psalm has been revealed..."
        elif content_style == 3:
            intro_text = "Fresh proverbs have been unearthed..."
        elif content_style == 4:
            intro_text = "A new parable has emerged..."
        elif content_style == 5:
            intro_text = "A new verse has been composed..."
        elif content_style == 6:
            intro_text = "A new jest has been discovered..."

        response = webhook_client.send(
            text=intro_text,
            blocks=blocks,
        )
        print("---- Slack responses ----")
        print(response)

    except SlackApiError as e:
        # Log the error
        print(f"Error sending Slack message: {e}")

if __name__ == "__main__":

    # variables for our book
    book_title = "The Books of John"

    emotions = [
        "love",
        "joy",
        "anger",
        "sadness",
        "fear",
        "surprise",
        "disgust",
        "envy",
        "hope",
        "hurt",
        "shame",
        "guilt",
        "pride",
        "desire",
        "nostalgia",
        "excitement",
        "enlightenment",
        "loneliness",
        "jealousy",
        "contentment",
        "satisfaction",
        "loathing",
        "despair",
        "passion",
        "yearning",
        "bitterness",
        "ambivalence",
        "melancholy",
        "resentment",
        "awe",
        "confusion",
        "anticipation",
        "tranquility",
        "happiness",
        "amusement",
        "absurdity",
        "whimsy",
        "outrage",
        "insanity",
        "hilarity",
        "euphoria",
        "gratitude",
        "serenity",
        "bliss",
        "exhilaration",
        "revelation"
    ]

    bro_dict = {

            "JP":
                {
                  "sex": "male",
                  "sex": "male",
                  "name": "JP",
                  "hair": "blonde",
                  "eyes": "blue",
                  "beard": False,
                },

            "Kris":
                {
                  "sex": "male",
                  "name": "Kris",
                  "hair": "blonde",
                  "eyes": "blue",
                  "beard": True
                },

            "Bilinski":
                {
                  "sex": "male",
                  "name": "Bilinski",
                  "hair": "blonde",
                  "eyes": "blue",
                  "beard": False
                },

            "Bobby":
                {
                  "sex": "male",
                  "name": "Bobby",
                  "hair": "long brown",
                  "eyes": "brown",
                  "beard": True
                },

            "Matt":
                {
                  "sex": "male",
                  "name": "Matt",
                  "hair": "short brown",
                  "eyes": "brown",
                  "beard": True
                },

            "Robert":
                {
                  "sex": "male",
                  "name": "Robert",
                  "hair": "red",
                  "eyes": "brown",
                  "beard": True
                },

            "Wells":
                {
                  "sex": "male",
                  "name": "Wells",
                  "hair": "short brown",
                  "eyes": "blue",
                  "beard": False
                },
            "Amy":
                {
                  "sex": "female",
                  "name": "Amy",
                  "hair": "long blonde",
                  "eyes": "brown",
                  "beard": False
                },
            "Brian":
                {
                  "sex": "male",
                  "name": "Brian",
                  "hair": "short brown",
                  "eyes": "brown",
                  "beard": True
                },
    }

    activities_list = [
        {
            "activity": "drinking whiskey",
            "bro_list": ["JP", "Kris", "Bilinski", "Bobby", "Matt", "Robert", "Wells", "Brian"],
            "chapter_title": "Whiskey",
        },
        {
            "activity": "playing golf",
            "bro_list": ["JP", "Kris", "Bilinski", "Bobby", "Matt", "Robert"],
            "chapter_title": "Tee Time",
        },
        {
            "activity": "gambling at the casino",
            "bro_list": ["JP", "Bilinski"],
            "chapter_title": "Rain Man",
        },
        {
            "activity": "watching sports",
            "bro_list": ["JP", "Kris", "Bilinski", "Brian"],
            "chapter_title": "The Sport",
        },
        {
            "activity": "playing blackjack",
            "bro_list": ["JP", "Bilinski"],
            "chapter_title": "Counting Cards",
        },
        {
            "activity": "throwing dice",
            "bro_list": ["JP", "Kris", "Bilinski"],
            "chapter_title": "Come 69",
        },
        {
            "activity": "delivering a huge, empty package to Amy",
            "bro_list": None,
            "chapter_title": "Tracking Numbers",
        },
        {
            "activity": "making cocktails",
            "bro_list": ["JP", "Kris", "Bilinski", "Bobby", "Matt", "Robert", "Wells", "Brian"],
            "chapter_title": "Mixology",
        },
        {
            "activity": "drinking beers",
            "bro_list": ["JP", "Kris", "Bilinski", "Bobby", "Matt", "Robert", "Wells", "Brian"],
            "chapter_title": "Drinking, Part 2",
        },
        {
            "activity": "enjoying craft beer",
            "bro_list": ["JP", "Kris", "Bilinski", "Bobby", "Matt", "Robert", "Wells", "Brian"],
            "chapter_title": "Fancy Drink",
        },
        {
            "activity": "investing in cryptocurrency",
            "bro_list": ["JP", "Bilinski", "Brian"],
            "chapter_title": "Examination of Cryptocurrency Microeconomics",
        },
        {
            "activity": "drinking wine",
            "bro_list": ["JP", "Kris", "Bilinski", "Bobby", "Matt", "Robert", "Wells", "Brian"],
            "chapter_title": "Side Wine",
        },
        {
            "activity": "telling long stories",
            "bro_list": None,
            "chapter_title": "Verbose Logging",
        },
        {
            "activity": "gaming the stock market",
            "bro_list": ["JP"],
            "chapter_title": "Stonks",
        },
        {
            "activity": "playing old nintendo games",
            "bro_list": ["JP", "Kris", "Brian"],
            "chapter_title": "8-bit Adventures",
        },
        {
            "activity": "jumping on the trampoline",
            "bro_list": ["JP", "Kris", "Brian"],
            "chapter_title": "The Dangers of Childhood",
        },
        {
            "activity": "being shirtless",
            "bro_list": ["JP", "Kris", "Bilinski", "Bobby", "Matt", "Robert", "Wells", "Brian"],
            "chapter_title": "FREEDOM",
        },
        {
            "activity": "smoking weed",
            "bro_list": ["JP", "Bobby", "Robert"],
            "chapter_title": "At 30,000 Ft",
        },
        {
            "activity": "slaying a beast named Amy",
            "bro_list": None,
            "chapter_title": "The Great Hunt",
        },
        {
            "activity": "playing slot machines",
            "bro_list": ["JP", "Kris", "Bilinski"],
            "chapter_title": "Grinding",
        },
        {
            "activity": "drinking and driving",
            "bro_list": ["JP", "Kris", "Bilinski", "Bobby", "Matt", "Robert", "Wells", "Brian"],
            "chapter_title": "Road Sodes",
        },
        {
            "activity": "getting nothing done",
            "bro_list": None,
            "chapter_title": "Fruitless Labor",
        },
        {
            "activity": "wiping a crack in the wrong direction, which gets some balls dirty",
            "bro_list": ["Bobby", "Wells"],
            "chapter_title": "C2S",
        },
        {
            "activity": "chillin in a hot tub",
            "bro_list": ["JP", "Kris", "Bilinski", "Bobby", "Matt", "Robert", "Wells", "Brian"],
            "chapter_title": "Hot Tub Tech 2",
        },
        {
            "activity": "celebrating",
            "bro_list": ["JP", "Kris", "Bilinski", "Bobby", "Matt", "Robert", "Wells"],
            "chapter_title": "Celebrate",
        },
        {
            "activity": "grilling a ny strip",
            "bro_list": ["JP", "Kris", "Bilinski", "Bobby", "Matt", "Robert", "Wells", "Brian"],
            "chapter_title": "MEAT",
        },
        {
            "activity": "trimming hedges for hours",
            "bro_list": None,
            "chapter_title": "Trimming the Hedges",
        },
        {
            "activity": "advocating for one of bernie sanders' economic, social, or foreign policies",
            "bro_list": None,
            "chapter_title": "Feel the Bern",
        },
    ]

    # Set your OpenAI API key
    client.api_key = OPENAI_API_KEY

    # Determine content style: command-line argument or random
    content_style = None
    is_dev_mode = False

    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg == "--dev":
                is_dev_mode = True
                print("Posting to development")
            elif arg == "--cs":
                try:
                    content_style = int(sys.argv[sys.argv.index(arg) + 1])
                    if content_style not in range(1, 7):
                        raise ValueError("Invalid content style. Please enter a number between 1 and 6.")
                except (ValueError, IndexError):
                    print("Invalid argument. Please provide a valid content style (1-6) after '--cs'.")
                    sys.exit(1)

    if content_style is None:
        content_style = random.randint(1, 6)

    print(CONTENT_STYLES[content_style])

    # Pick a random emotion
    theme = random.choice(emotions)

    # Storing activity number as the chapter number
    activity_number = random.randint(0, len(activities_list) - 1)
    activity_data = activities_list[activity_number]
    activity_data['chapter_number'] = activity_number + 1  # Add chapter number to activity data

    # Get a bro (or not) to bro with
    bros = activity_data["bro_list"]
    if bros:
        bro_key = random.choice(bros)
        bro = bro_dict[bro_key]

        bro_gpt_text = f" with his bro {bro['name']}"

        if bro['beard']:
            bro_dalle_text = f" with his bro {bro['name']} ({bro['sex']}, {bro['hair']} hair, {bro['eyes']} eyes, with beard)"
        else:
            bro_dalle_text = f" with his bro {bro['name']} ({bro['sex']}, {bro['hair']} hair, {bro['eyes']} eyes, clean-shaven)"
    else:
        bro_gpt_text = ""
        bro_dalle_text = ""
        bro = None


    # Random number of verses and starting verse (if applicable)
    starting_verse = None
    number_verses = None
    if content_style == 1:  # Book/Chapter
        starting_verse = random.randint(1, 995)
        number_verses = random.randint(2, 4)
        ending_verse = starting_verse + (number_verses - 1)
        str_numbers = f"{starting_verse} - {ending_verse}"
    elif content_style in [2, 4, 5, 6]: #Psalm/Parable/Peom/Jest
        str_numbers = random.randint(1, 10000)
    elif content_style == 3: #Proverb
        str_numbers = f"{random.randint(1, 100), random.randint(200, 500), random.randint(4000, 10000)}" 

    # Generate GPT prompt
    gpt_prompt = get_gpt_prompt(content_style, theme, activity_data, bro_gpt_text, number_verses, starting_verse)

    # Generate GPT story
    story = generate_gpt_story(gpt_prompt, content_style)

    # Generate DALL-E prompt (if applicable)
    dalle_prompt = generate_dalle_prompt(story, bro_dalle_text, content_style)

    # Generate DALL-E image (if applicable)
    generate_image(dalle_prompt, bro)

    # store to imgur
    imgur_url = upload_image_to_imgur()

    # Generate cocktail recipe (if applicable)
    cocktail_recipe = generate_cocktail_recipe(theme, activity_data)

    # Get webhook client
    webhook_client = get_webhook_client(is_dev_mode)

    # Send Slack message
    send_slack_message(webhook_client, story, theme, activity_data, imgur_url, cocktail_recipe, content_style, str_numbers)
