import os
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

# Replace with your Bot's token
BOT_TOKEN = "7197334579:AAFchgcg6HIkUe33awT0cqTJkMENwcWid0k"
GITHUB_REPO = "https://api.github.com/repos/kingbackbro/legendyt/contents/approved_ids.txt"  # GitHub file link

# Dictionary to store Android ID approval status
pending_approval_ids = {}

def start(update, context):
    """Telegram start command"""
    # User ke Android ID ko retrieve karke approval ke liye bhejna
    user_id = update.message.from_user.id
    android_id = update.message.text.split(":")[1].strip()  # Extract Android ID from the message
    pending_approval_ids[android_id] = "pending"  # Mark as pending approval

    keyboard = [
        [
            InlineKeyboardButton("Yes", callback_data=f"approve_yes_{android_id}"),
            InlineKeyboardButton("No", callback_data=f"approve_no_{android_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(f"Do you approve the Android ID: {android_id}?", reply_markup=reply_markup)

def button(update, context):
    """Handle the approval response"""
    query = update.callback_query
    android_id = query.data.split('_')[2]  # Extract Android ID from callback data
    approval_status = query.data.split('_')[1]  # Extract approval status (yes or no)
    
    # Update the approval status
    if approval_status == "yes":
        pending_approval_ids[android_id] = "approved"
        query.edit_message_text(text=f"Android ID {android_id} approved.")

        # Update the GitHub file to reflect approval
        update_github_status(android_id, "approved")
    else:
        pending_approval_ids[android_id] = "denied"
        query.edit_message_text(text=f"Android ID {android_id} denied.")

        # Update the GitHub file to reflect denial
        update_github_status(android_id, "denied")

def update_github_status(android_id, status):
    """Update the approval status in the GitHub file"""
    headers = {
        'Authorization': 'token YOUR_GITHUB_TOKEN',  # Personal access token from GitHub
        'Accept': 'application/vnd.github.v3+json'
    }

    # Fetch the current content of the approved_ids.txt file from GitHub
    response = requests.get(GITHUB_REPO, headers=headers)
    if response.status_code == 200:
        file_data = response.json()
        current_content = file_data['content']
        decoded_content = requests.utils.unquote(current_content)  # Decode the base64 content
        
        # Add the Android ID with approval status to the content
        updated_content = decoded_content + f"\n{android_id}: {status}"

        # Prepare data to update the file on GitHub
        update_data = {
            "message": "Update approval status",
            "content": updated_content.encode('utf-8').decode('utf-8'),
            "sha": file_data['sha'],  # Get current sha to update the file
        }

        # GitHub API to update file
        update_response = requests.put(GITHUB_REPO, headers=headers, json=update_data)
        if update_response.status_code == 200:
            print("GitHub file updated successfully.")
        else:
            print(f"Failed to update GitHub file: {update_response.status_code}")
    else:
        print("Failed to fetch the current GitHub file")

def main():
    """Start the bot and handle commands"""
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
