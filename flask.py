from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from discord_bot import DiscordController
import os

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

@app.route('/api/verify', methods=['POST'])
def verify():
    """التحقق من توكن البوت"""
    data = request.json
    token = data.get('token')
    
    controller = DiscordController(token)
    result = controller.verify()
    
    if result['success']:
        guilds = controller.get_guilds()
        return jsonify({
            'success': True,
            'bot': result['bot'],
            'guilds': guilds
        })
    else:
        return jsonify({
            'success': False,
            'error': result.get('error', 'Invalid token')
        })

@app.route('/api/execute', methods=['POST'])
def execute():
    """تنفيذ الأوامر"""
    data = request.json
    token = data.get('token')
    command = data.get('command')
    guild_id = data.get('guild_id')
    params = data.get('params', {})
    
    controller = DiscordController(token)
    
    try:
        if command == 'createChannels':
            result = controller.create_channels(
                guild_id, 
                int(params.get('count', 10)), 
                params.get('name', 'nuked')
            )
        elif command == 'deleteChannels':
            result = controller.delete_channels(guild_id)
        elif command == 'banAll':
            result = controller.ban_all(guild_id)
        elif command == 'deleteRoles':
            result = controller.delete_roles(guild_id)
        elif command == 'createRoles':
            result = controller.create_roles(
                guild_id, 
                int(params.get('count', 10)), 
                params.get('name', 'nuked')
            )
        elif command == 'spam':
            result = controller.spam_channels(
                guild_id, 
                params.get('message', '@everyone NUKED'), 
                int(params.get('count', 5))
            )
        elif command == 'nuke':
            result = controller.nuke(guild_id)
        else:
            return jsonify({'success': False, 'error': 'Unknown command'}), 400
        
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)