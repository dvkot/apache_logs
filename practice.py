from flask import Flask, request, jsonify
import sqlite3
import configparser
from datetime import datetime

conn = sqlite3.connect('access_logs.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS access_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT,
        date TEXT,
        request TEXT,
        status INTEGER,
        bytes INTEGER
    )
''')
conn.commit()

def create_app():
    app = Flask(__name__)

    #config = configparser.ConfigParser()
    #config.read(configur)
    #file_path = config.get('LogsConfig', 'file_path')
    #format = config.get('LogsConfig', 'format')

    @app.route('/get_logs', methods=['GET'])
    def get_logs():
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        ip = request.args.get('ip')
        status = request.args.get('status')
    

        conn = sqlite3.connect('access_logs.db')
        cursor = conn.cursor()
    
        query = "SELECT * FROM access_logs WHERE 1=1"
        if date_from:
            query += f" AND date >= '{date_from}'"
        if date_to:
            query += f" AND date <= '{date_to}'"
        if ip:
            query += f" AND ip = '{ip}'"
        if status:
            query += f" AND status = '{status}'"

        try:
            cursor.execute(query)
            data = cursor.fetchall()
        except:
            print('Произошла ошибка. Убедитесь, что параметры записаны в виде словаря')
        

        conn.close()
    
        formatted_data = []
        for log in data:
            formatted_log = {
            "ip": log[1],
            "date": log[2],
            "request": log[3],
            "status": log[4],
            "bytes": log[5]
            }
            formatted_data.append(formatted_log)
            
        
        return jsonify(formatted_data)
    return app

app = create_app()

if __name__ == '__main__':
    

    def parse_logs(log_data):
        logs = log_data.split('\n')

        for log in logs:
            if log:
                data = log.split()
                if len(data) >= 10:
                    ip = data[0]
                    date_str = data[3][1:] + ' ' + data[4][:-1]
                    date = datetime.strptime(date_str, '%d/%b/%Y:%H:%M:%S %z')
                    request = data[5] + ' ' + data[6] + ' ' + data[7]
                    status = int(data[8])
                    bytes_sent = int(data[9])

                    cursor.execute('''
                        INSERT INTO access_logs (ip, date, request, status, bytes)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (ip, date, request, status, bytes_sent))
    
        conn.commit()
    
    def file_read(path):
        try:
            with open(path, 'r') as file:
                log_data = file.read()
                parse_logs(log_data)
        except:
            print('Файл не был найден')
                

        

    def view_logs(date_from=None, date_to=None, ip=None, status=None):
        try:    
            query = 'SELECT * FROM access_logs WHERE 1 = 1 '
            params = []
        
        
            if date_from:
                query += ' AND date >= ?'
                params.append(date_from)

            if date_to:
                query += ' AND date <= ?'
                params.append(date_to)

            if ip:
                query += ' AND ip = ?'
                params.append(ip)

            if status:
                query += ' AND status = ?'
                params.append(status)

            cursor.execute(query, params)
            records = cursor.fetchall()
            print(records)
        
        except sqlite3.Error as e:
            print(f'Произошла ошибка {e} во время выполнения запроса')
            
        except Exception as ex:
            print(f'Произошла ошибка {ex}')
        

        



def generate_get_logs_link(params=None):
    base_url = 'http://localhost:5000/get_logs'
    if params != None:
        query_params = '&'.join([f"{key}={value}" for key, value in params.items()])
        link = f"{base_url}?{query_params}"
    else:
        link = f"{base_url}"
    
    print(link)
    app.run()

