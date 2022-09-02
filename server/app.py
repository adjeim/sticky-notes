import os
from flask import Flask, send_from_directory, request
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_SYNC_SERVICE_SID = os.environ.get('TWILIO_SYNC_SERVICE_SID')
TWILIO_SYNC_LIST_SID = os.environ.get('TWILIO_SYNC_LIST_SID')

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
sync_list = client.sync.v1.services(TWILIO_SYNC_SERVICE_SID).sync_lists(TWILIO_SYNC_LIST_SID)

# Utility function to get the items for a specific sync list
def get_sync_list():
    sync_list_items = sync_list.sync_list_items.list()
    return [{'index': record.index, 'text': record.data.get('text')} for record in sync_list_items]


# Path for the main Svelte page: index.html
@app.route('/')
def root():
    return send_from_directory('../client/dist', 'index.html')


# Path for the rest of the static files (JS/CSS, etc.)
@app.route('/<path:path>')
def assets(path):
    return send_from_directory('../client/dist', path)

#  Get the list of sticky notes
@app.route('/notes', methods=['GET'])
def get_sticky_notes():
    sticky_notes = get_sync_list()
    return {'sticky_notes': sticky_notes}

#  Create a new sticky note
@app.route('/notes', methods=['POST'])
def create_sticky_note():
    data = request.get_json(force=True)
    text = data.get('text')

    sync_list_item = sync_list.sync_list_items.create(data={'text': text })

    return {
        'sticky_note': {'index': sync_list_item.index, 'text': sync_list_item.data.get('text')}
    }

#  Delete a specific sticky note
@app.route('/notes/<index>', methods=['DELETE'])
def delete_sticky_note(index):
    index = int(index)
    sync_list.sync_list_items(index).delete()
    return {'deleted': index }


if __name__ == '__main__':
    app.run(debug=True)