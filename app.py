import json
from flask import Flask, request, jsonify, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Инициализация приложения и лимитера
app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app, default_limits=["100 per day"])

# Загрузка данных из файла
def load_data():
    try:
        with open('data.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Сохранение данных в файл
def save_data(data):
    with open('data.json', 'w') as file:
        json.dump(data, file, indent=4)

# Загружаем данные при старте
data = load_data()

# Маршрут для сохранения ключа-значения
@app.route('/set', methods=['POST'])
@limiter.limit("10/minute")  # Ограничение на 10 запросов в минуту
def set_value():
    key = request.json.get('key')
    value = request.json.get('value')

    if not key or value is None:
        return jsonify({"error": "Missing key or value"}), 400

    # Сохраняем данные
    data[key] = value
    save_data(data)

    return jsonify({"message": "Key-value pair set successfully"}), 200

# Маршрут для получения значения по ключу
@app.route('/get/<key>', methods=['GET'])
def get_value(key):
    value = data.get(key)
    if value is None:
        return jsonify({"error": "Key not found"}), 404
    return jsonify({"key": key, "value": value}), 200

# Маршрут для удаления ключа
@app.route('/delete/<key>', methods=['DELETE'])
@limiter.limit("10/minute")  # Ограничение на 10 запросов в минуту
def delete_key(key):
    if key in data:
        del data[key]
        save_data(data)
        return jsonify({"message": "Key deleted successfully"}), 200
    return jsonify({"error": "Key not found"}), 404

# Маршрут для проверки существования ключа
@app.route('/exists/<key>', methods=['GET'])
def exists_key(key):
    if key in data:
        return jsonify({"exists": "the key exists"}), 200
    return jsonify({"exists": "the key does not exist"}), 200

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)
