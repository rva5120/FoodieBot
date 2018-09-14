import os
import time
import re
import random
from datetime import datetime

from slackclient import SlackClient


# Instantiate Slack Client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

# Lunch Bot User ID
lunch_bot_id = None

# Constants
RTM_READ_DELAY = 1	# 1 sec delay between reading from RTM
LUNCH_COMMAND = "lunch"
WHERE_COMMAND = "where"
PLACES_COMMAND = "places"
LIST_COMMAND = "list"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
RESTAURANTS = ["Au Bon Pain (Kern Blgd)", "Pho11", "Noodles & Co.", "Subway", "Starbucks", "Little Scheshuan", "Qdoba","Margarita\'s Pizza", "California Tortilla", "Doan\'s Bones", "John\'s Shanghai", "Five Guys", "Cafe 210", "Tadashi", "Federal Taphouse" , "Green Bowl", "Penn Pide", "Fiddlehead", "Burger King (HUB)", "Chik-fil-A (HUB)", "Sbarro (HUB)", "Panda Express (HUB)", "HUB Soups and Garden", "Blue Burrito (HUB)", "Grate Chee (HUB)", "McAlister\'s Deli", "Mixed Greens (HUB)","Hibachi-San (HUB)" ,"Sauly Boy\'s", "Jersey Mike\'s", "Kondu", "Panera Bread", "Champs", "Irving\'s", "Kaarma", "Cozy Thai", "Shaker\'s Grill Food Cart", "Yallah Taco", "India Pavilion", "Underground", "Canyon", "Taco Bell", "Chipotle...", "Waker Chicken", "Yummy Cafe", "McLanahans", "The Deli & Z Bar", "Primanti Bros.", "The Waffle Shop", "Big Bowl", "Penn Kebab", "Jimmy John\'s", "McDonals\'s", "Are U Hungry", "Beijing", "Mad Mex"]

# Generate random seed
random_num = random.seed(datetime.now())
print("Random Seed..." + str(random_num))



###
# Aux Functions
###
def parse_bot_commands(slack_events):

	for event in slack_events:

		# Get the command
		if event["type"] == "message" and not "subtype" in event:
			matches = re.search(MENTION_REGEX, event["text"])
		else:
			matches = None

		# If a command was given, extract it
		if matches:
			user_id = matches.group(1)
			message = matches.group(2).strip()
		else:
			user_id = None
			message = None

		if user_id == lunch_bot_id:
			return message, event["channel"]
		else:
			return None, None


def send_response_back(response, channel):

	# Send response back to the channel
	slack_client.api_call("chat.postMessage",
				channel = channel,
				text = response)

def send_restaurant_list(channel):

	restaurants = ", ".join(RESTAURANTS)
	response = "Here is a list of restaurants that I consider: \n" + restaurants
	send_response_back(response, channel)


def send_lunch_suggestions(channel):

	# Chosen restaurant
	choice = random.choice(RESTAURANTS)
	print("Index choice..." + str(choice))
	#print("Restaurant chosen..." + str(restaurant))
	
	# Suggest random restaurant
	suggestion = "Today\'s suggestion is... " + choice + "."

	if "Chipotle" in choice or "Qdoba" in choice:
		new_choice = random.choice(RESTAURANTS)
		if "Chipotle" in new_choice or "Qdoba" in new_choice:
			new_choice = random.choice(RESTAURANTS)
		suggestion = suggestion + " But a better choice might be " + new_choice + " instead..."

	# Send suggestion back to the channel
	send_response_back(suggestion, channel)


def send_unknown_response(channel):

	# Craft response
	response = "I only know lunch places... but you can ask my developer to teach me new things."
	
	# Send response
	send_response_back(response, channel)



###
# Start...
###
if __name__ == "__main__":

	# Connect to Slack
	if slack_client.rtm_connect(with_team_state=False):

		print("Lunch Bot connected and running!")

		# Read the bot's user ID
		lunch_bot_id = slack_client.api_call("auth.test")["user_id"]

		# Listen for users requesting the bot's input
		while True:

			# Read command and channel of the message
			user_input = slack_client.rtm_read()
			
			# If the user made a request, respond
			if user_input != []:
				# Get command and channel
				command, channel = parse_bot_commands(user_input)
			
				# Process command and respond
				if command:
					command = command.lower()
					if PLACES_COMMAND in command or LIST_COMMAND in command:
						send_restaurant_list(channel)
					elif LUNCH_COMMAND in command or WHERE_COMMAND in command:
						send_lunch_suggestions(channel)
					else:
						send_unknown_response(channel)

			time.sleep(RTM_READ_DELAY)

	else:
		print("Lunch Bot failed to connect...")
