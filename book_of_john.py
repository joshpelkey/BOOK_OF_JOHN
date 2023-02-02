# Import the necessary package
import sys
import random
import openai
from slack_sdk.webhook import WebhookClient
import requests
import subprocess
from urlextract import URLExtract

# these are my api keys and stuff, hidden from git
import keys

# home dir /home/name
home_dir = keys.home_dir

# you're path for image
img_path = keys.img_path

# Authenticate with OpenAI using your API key
openai.api_key = keys.openai_api_key

# no args, post to prod
if len(sys.argv) < 2:
 
    print ("posting to prod")
    # ai_stories slack
    client = WebhookClient(
        "https://hooks.slack.com/services/" + keys.slack_ai_key
    )

#if --dev arg, post to my own channel
elif sys.argv[1] == "--dev":
    print ("posting to dev")

    # me slack
    client = WebhookClient(
        "https://hooks.slack.com/services/" + keys.slack_dev_key
    )

# you did something weird
else:
    print ("you provided args, but they don't work")
    sys.exit()

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
]

activities_list = [
    {
        "activity": "drinking whiskey",
        "dall_e": "drinking whiskey",
        "chapter_title": "Whiskey",
    },
    {
        "activity": "playing golf",
        "dall_e": "playing golf",
        "chapter_title": "Tee Time",
    },
    {
        "activity": "gambling at the casino",
        "dall_e": "sitting at a card table",
        "chapter_title": "Mathematics",
    },
    {
        "activity": "watching sports",
        "dall_e": "watching sports",
        "chapter_title": "The Sport",
    },
    {
        "activity": "playing blackjack",
        "dall_e": "playing cards",
        "chapter_title": "Counting Cards",
    },
    {
        "activity": "throwing dice",
        "dall_e": "throwing dice",
        "chapter_title": "Come 69",
    },
    {
        "activity": "delivering packages",
        "dall_e": "delivering packages",
        "chapter_title": "Kama Sutra",
    },
    {
        "activity": "making cocktails",
        "dall_e": "mixing drinks",
        "chapter_title": "Mixology",
    },
    {
        "activity": "drinking beers",
        "dall_e": "drinking",
        "chapter_title": "Drinking, Part 2",
    },
    {
        "activity": "enjoying craft beer",
        "dall_e": "drinking at a bar",
        "chapter_title": "Fancy Drink",
    },
    {
        "activity": "investing in cryptocurrency",
        "dall_e": "cryptocurrency",
        "chapter_title": "Examination of Cryptocurrency Microeconomics",
    },
    {
        "activity": "drinking wine",
        "dall_e": "drinking wine",
        "chapter_title": "Side Wine",
    },
    {
        "activity": "telling long stories",
        "dall_e": "telling long stories",
        "chapter_title": "Word of Art",
    },
    {
        "activity": "gaming the stock market",
        "dall_e": "investing in the stock market",
        "chapter_title": "Stonks",
    },
    {
        "activity": "playing old nintendo games",
        "dall_e": "playing old nintendo games",
        "chapter_title": "8-bit Adventures",
    },
    {
        "activity": "jumping on the trampoline",
        "dall_e": "jumping on the trampoline",
        "chapter_title": "The Dangers of Childhood",
    },
    {
        "activity": "being shirtless",
        "dall_e": "being shirtless",
        "chapter_title": "FREEDOM",
    },
    {
        "activity": "smoking weed",
        "dall_e": "smoking",
        "chapter_title": "At 30,000 Ft",
    },
    {
        "activity": "slaying a beast",
        "dall_e": "hunting",
        "chapter_title": "The Great Hunt",
    },
    {
        "activity": "playing slot machines",
        "dall_e": "slot machines",
        "chapter_title": "Grinding",
    },
    {
        "activity": "drinking and driving",
        "dall_e": "drinking in the car",
        "chapter_title": "Road Sodes",
    },
    {
        "activity": "getting nothing done",
        "dall_e": "boredom",
        "chapter_title": "Fruitless Labor",
    },
]

bros = ["", "", "", " with his bro JP", " with his bro Kris"]


# pick a randoms
theme = random.choice(emotions)

activity_number = random.randint(
    0, 
    len(activities_list) - 1
)

activity_dict = activities_list[activity_number]
number_verses = random.randint(3, 7)
starting_verse_number = random.randint(1, 993)

# set your prompt with all variables
gpt_prompt = (
    "Tell me an overly descriptive story about John "
    + activity_dict["activity"]
    + random.choice(bros)
    + " with the theme of "
    + theme
    + " in "
    + str(number_verses)
    + " sentences. "
    + "Number each sentence, starting with "
    + str(starting_verse_number)
    + ". For example, "
    + str(starting_verse_number)
    + ": Your first sentence goes here."
)

print(gpt_prompt)

# Ask ChatGPT your question
chat_response = openai.Completion.create(
    engine="text-davinci-003", prompt=gpt_prompt, temperature=0.75, max_tokens=2048
)
# DALL-E prompt
dalle_prompt = "a painting of " + activity_dict["dall_e"] + " with influence from a famous work about " + theme

# generate a dope DALL-E image
dalle_response = openai.Image.create(prompt=dalle_prompt, size="256x256")
image_url = dalle_response["data"][0]["url"]

# get the image and store it on imgur
img_data = requests.get(image_url).content
with open(home_dir  + img_path, "wb") as handler:
    handler.write(img_data)

imgur = subprocess.run(
    [home_dir + "/.local/bin/imgur-uploader", home_dir + img_path],
    stdout=subprocess.PIPE,
)

extractor = URLExtract()
imgur_str = str(imgur)
url = extractor.find_urls(imgur_str)

clean_url = url[0][:-4]


# Send the response to the incoming Slack webhook
slack_response = client.send(
    text="a daily reading from THE BOOKS OF JOHN...",
    blocks=[
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
                    "text": "Book of "
                    + theme.capitalize()
                    + " | _Chapter "
                    + str(activity_number + 1)
                    + ": "
                    + activity_dict['chapter_title'] 
                    + " | Verses "
                    + str(starting_verse_number)
                    + "-"
                    + str(starting_verse_number + (number_verses - 1))
                    + "_",
                    "type": "mrkdwn",
                }
            ],
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": chat_response["choices"][0]["text"]},
        },
        {
            "type": "image",
            "title": {
                "type": "plain_text",
                "text": "["
                + theme.capitalize()
                + " - Chapter "
                + str(activity_number + 1)
                + ": "
                + activity_dict["chapter_title"]
                + "]",
                "emoji": True,
            },
            "image_url": clean_url,
            "alt_text": "[ THE BOOKS OF JOHN || "
            + theme.capitalize()
            + " - Chapter "
            + str(activity_number + 1)
            + ": "
            + activity_dict["chapter_title"]
            + " ]",
        },
    ],
)

print(chat_response)
print(dalle_response)
print(slack_response)
