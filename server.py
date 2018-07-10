import chat
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def index_route():
	if not request.is_json:
		print('Input not json')
		return ''
	json = request.get_json()
	[input_type, result, topic] = chat.chat(json['text'], json['topic'])
	return jsonify({
		'type': input_type,
		'content': result,
		'topic': topic
	})

if __name__ == '__main__':
	app.run(host='127.0.0.1', port=5000, debug=True)