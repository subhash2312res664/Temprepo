# ✅This is the fine working code: ✅
#fusion photography bot

import telebot
from telebot import types


# Replace this with your bot's API token
Token = '7224337547:AAGpvRMXAX_td1lQfe0F2SIaYKy4-IhA6wo' #fusion photography bot
bot = telebot.TeleBot(Token)

# Replace this with the admin's user ID
ADMIN_ID = 1469030399  # indiansubhashkumar telegram id (1368295198) #username(@indiansubhashkumar)
# username: @itz_pr_14 ID: (1469030399)

# Replace this with your group chat ID
GROUP_CHAT_ID = -1002194672193  # Change this to the actual group chat ID
TOPIC_ID = 16  # Initialize with None, you will set this after retrieving the ID

# Define states
STATE_QUERY, STATE_NAME, STATE_BATCH, STATE_LOCATION, STATE_DATE, STATE_PHOTO = range(6)
user_states = {}

def set_user_state(user_id, state):
    user_states[user_id] = state

def get_user_state(user_id):
    return user_states.get(user_id, STATE_QUERY)

# Store user data and pending approvals
user_data = {}
pending_approvals = {}

def initialize_user_data(user_id):
    if user_id not in user_data:
        user_data[user_id] = {}

# Handlers
@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type == 'private':  # Check for group chat
        bot.reply_to(message,
                     f" /photography : to add photos.\n"
                     f" /help : Commands list\n"
                     f" /coordinator : Coordinator support.\n"
                     )

        @bot.message_handler(commands=['help'])
        def help(message):
            bot.reply_to(message,
                         f"/start : Start the Bot\n"
                         f"/photography : to add photos.\n"
                         f"/help : Commands list.\n"
                         f"/coordinator : Coordinator support."
                         )

        @bot.message_handler(commands=['coordinator'])
        def coordinator(message):
            bot.reply_to(message, 'Contact the coordinator at @itz_pr_14.')

        @bot.message_handler(commands=['photography'])
        def handle_photoAndQuery(message):
            bot.reply_to(message, 'Please enter your name:')
            set_user_state(message.chat.id, STATE_NAME)

        @bot.message_handler(func=lambda message: get_user_state(message.chat.id) == STATE_NAME)
        def handle_name(message):
            user_id = message.chat.id
            initialize_user_data(user_id)
            user_data[user_id]['name'] = message.text
            bot.reply_to(message, 'Please enter your batch (ex-1,2,..):')
            set_user_state(user_id, STATE_BATCH)

        @bot.message_handler(func=lambda message: get_user_state(message.chat.id) == STATE_BATCH)
        def handle_name(message):
            user_id = message.chat.id
            initialize_user_data(user_id)
            user_data[user_id]['batch'] = message.text
            bot.reply_to(message, 'Please enter the location where the photo was taken:')
            set_user_state(user_id, STATE_LOCATION)

        @bot.message_handler(func=lambda message: get_user_state(message.chat.id) == STATE_LOCATION)
        def handle_location(message):
            user_id = message.chat.id
            user_data[user_id]['location'] = message.text
            bot.reply_to(message, 'Please enter the date when the photo was taken (ex: 7th July, 24):')
            set_user_state(user_id, STATE_DATE)

        @bot.message_handler(func=lambda message: get_user_state(message.chat.id) == STATE_DATE)
        def handle_date(message):
            user_id = message.chat.id
            user_data[user_id]['date'] = message.text
            bot.reply_to(message, 'Please send the photo:')
            set_user_state(user_id, STATE_PHOTO)

        @bot.message_handler(content_types=['photo'],
                             func=lambda message: get_user_state(message.chat.id) == STATE_PHOTO)
        def handle_photo(message):
            user_id = message.chat.id
            photo_file = message.photo[-1].file_id
            user_data[user_id]['photo'] = photo_file

            # Store the pending approval request
            pending_approvals[user_id] = user_data[user_id]

            # Notify admin
            user_info = user_data[user_id]
            approval_text = (f"New photo submission:\nName: {user_info['name']}\nBatch:{user_info['batch']}\n"
                             f"Location: {user_info['location']}\nDate: {user_info['date']}\n")

            approval_markup = types.InlineKeyboardMarkup()
            approval_markup.add(types.InlineKeyboardButton("Approve", callback_data=f"approve_{user_id}"))
            approval_markup.add(types.InlineKeyboardButton("Reject", callback_data=f"reject_{user_id}"))

            bot.send_photo(ADMIN_ID, photo_file, caption=approval_text, reply_markup=approval_markup)

            bot.reply_to(message, 'Your photo has been submitted for verification.')
            set_user_state(user_id, STATE_QUERY)  # Reset state after submission

        @bot.callback_query_handler(
            func=lambda call: call.data.startswith('approve_') or call.data.startswith('reject_'))
        def handle_approval(call):
            action, user_id = call.data.split('_')
            user_id = int(user_id)

            if action == 'approve':
                bot.send_message(user_id,
                                 f"Your photo submission has been approved!")
                # Send photo to the specific topic in the group chat
                if user_id in pending_approvals and TOPIC_ID is not None:
                    user_info = pending_approvals[user_id]
                    approval_text = (f"Name: {user_info['name']}\nBatch: {user_info['batch']}\n"
                                     f"Location: {user_info['location']}\nDate: {user_info['date']}\n")
                    bot.send_photo(GROUP_CHAT_ID, user_info['photo'], caption=approval_text, message_thread_id=TOPIC_ID)

                    bot.reply_to(message,
                                 f"/start : Start the Bot\n"
                                 f"/photography : to add photos.\n"
                                 f"/help : Commands list.\n"
                                 f"/coordinator : Coordinator support."
                                 )

            elif action == 'reject':
                bot.send_message(user_id, "Your photo submission has been rejected.")
                bot.reply_to(message,
                             f"/start : Start the Bot\n"
                             f"/photography : to add photos.\n"
                             f"/help : Commands list.\n"
                             f"/coordinator : Coordinator support."
                             )

            # Remove the pending approval
            if user_id in pending_approvals:
                del pending_approvals[user_id]

            # Notify the admin of the action
            bot.answer_callback_query(call.id, f"Submission {'approved' if action == 'approve' else 'rejected'}.")

    else:
        bot.reply_to(message,
                     f"This command cannot be used in groups. Please start a private chat with the bot.\n"
                     f"@fusion_photography_bot."
                     )
        # return  # Exit the function if in a group



bot.polling()
