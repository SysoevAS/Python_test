from flask import Flask, request, jsonify, g
from flask_httpauth import HTTPBasicAuth
import pandas as pd

app = Flask(__name__)
auth = HTTPBasicAuth()

# Имитация базы данных пользователей
users = {
    "username": "password"
}

# Список загруженных файлов
uploaded_files = {}


@auth.verify_password
def verify_password(username, password):
    if username in users and password == users[username]:
        g.current_user = username
        return True
    return False


@app.route('/upload', methods=['POST'])
@auth.login_required
def upload_file():
    file = request.files['file']

    # Сохранение загруженного файла
    df = pd.read_csv(file)
    file_id = len(uploaded_files) + 1
    uploaded_files[file_id] = df

    response = {'file_id': file_id}
    return jsonify(response)


@app.route('/files', methods=['GET'])
@auth.login_required
def get_files():
    files = [{'file_id': file_id, 'columns': list(df.columns)} for file_id, df in uploaded_files.items()]
    return jsonify(files)


@app.route('/data', methods=['GET'])
@auth.login_required
def get_data():
    file_id = int(request.args.get('file_id'))
    columns = request.args.getlist('columns[]')

    if file_id not in uploaded_files:
        return 'File not found', 404

    df = uploaded_files[file_id]

    # Фильтрация данных
    for column in columns:
        column_name, filter_value = column.split(':')
        filter_value = int(filter_value)  # Здесь можно задать конвертацию в нужный тип данных

        df = df[df[column_name] == filter_value]

    # Сортировка данных
    sort_by = request.args.get('sort_by')
    if sort_by:
        df = df.sort_values(by=sort_by)

    # Преобразование данных в формат JSON
    data = df.to_dict(orient='records')

    return jsonify(data)


@app.route('/delete', methods=['DELETE'])
@auth.login_required
def delete_file():
    file_id = int(request.args.get('file_id'))

    if file_id not in uploaded_files:
        return 'File not found', 404

    del uploaded_files[file_id]

    return 'File deleted'


if __name__ == '__main__':
    app.run()
