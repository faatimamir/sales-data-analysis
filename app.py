from flask import Flask, request, jsonify, render_template
from data_ingestion import load_data
from llm_integration import (
    get_performance_feedback,
    get_team_performance,
    get_sales_trends_and_forecasting
)
import os
import pandas as pd
from flask_cors import CORS
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

data_storage = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/load_data', methods=['POST'])
def load_data_endpoint():
    file = request.files.get('file')
    if file:
        file_path = os.path.join('./uploads', file.filename)
        os.makedirs('./uploads', exist_ok=True)
        logging.debug(f'Saving file to: {file_path}')
        file.save(file_path)
        try:
            global data_storage
            logging.debug('Loading data from file...')
            data_storage = load_data(file_path)
            logging.debug(f'Data loaded successfully. Data storage: {data_storage}')
            return jsonify({'message': 'Data loaded successfully'}), 200
        except ValueError as e:
            logging.error(f'ValueError: {str(e)}')
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logging.error(f'Exception: {str(e)}')
            return jsonify({'error': 'An error occurred while loading data'}), 500
    else:
        logging.error('No file provided')
        return jsonify({'error': 'No file provided'}), 400

@app.route('/api/performance_feedback', methods=['GET'])
def performance_feedback_endpoint():
    unit_id = request.args.get('unit_id')
    logging.debug(f'Received request for performance feedback. unit_id: {unit_id}')
    if data_storage and unit_id:
        try:
            feedback = get_performance_feedback(data_storage, unit_id)
            logging.debug(f'Performance feedback: {feedback}')
            return jsonify({'feedback': feedback}), 200
        except Exception as e:
            logging.error(f'Exception: {str(e)}')
            return jsonify({'error': 'An error occurred while getting performance feedback'}), 500
    else:
        logging.error('No data loaded or unit_id missing')
        return jsonify({'error': 'No data loaded or unit_id missing'}), 400

@app.route('/api/team_performance', methods=['GET'])
def team_performance_endpoint():
    logging.debug('Received request for team performance')
    if data_storage:
        try:
            performance = get_team_performance(data_storage)
            logging.debug(f'Team performance: {performance}')
            return jsonify({'performance': performance}), 200
        except Exception as e:
            logging.error(f'Exception: {str(e)}')
            return jsonify({'error': 'An error occurred while getting team performance'}), 500
    else:
        logging.error('No data loaded')
        return jsonify({'error': 'No data loaded'}), 400

@app.route('/api/sales_trends', methods=['GET'])
def sales_trends_and_forecasting_endpoint():
    logging.debug('Received request for sales trends and forecasting')
    if data_storage:
        try:
            results = get_sales_trends_and_forecasting(data_storage)
            logging.debug(f'Sales trends and forecasting results: {results}')
            return jsonify({'results': results}), 200
        except Exception as e:
            logging.error(f'Exception: {str(e)}')
            return jsonify({'error': 'An error occurred while getting sales trends and forecasting'}), 500
    else:
        logging.error('No data loaded')
        return jsonify({'error': 'No data loaded'}), 400
if __name__ == '__main__':
    app.run(debug=True)
