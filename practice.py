from flask import Flask, request, jsonify
import sqlite3
import apache_log_parser
from datetime import datetime

conn = sqlite3.connect('access_logs.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS access_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT,
        logname TEXT,
        user TEXT,
        date TimeStamp,
        request TEXT,
        status INTEGER,
        bytes INTEGER
    )
''')
conn.commit()

def create_app():
    app = Flask(__name__)
    


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
            "date": log[4],
            "request": log[5],
            "status": log[6],
            "bytes": log[7]
            }
            formatted_data.append(formatted_log)
            
        
        return jsonify(formatted_data)
    return app

app = create_app()

if __name__ == '__main__':
    

    def parse_logs(log_data):

        with open('logs/config.ini', 'r') as file:
            lines = file.readlines()

        for line in lines:
            if line.startswith('format:'):
                format_value = line[len('format:'):].strip()
                format_value = format_value[1:-1]
                break

        print("Значение format из файла config.ini:", format_value)
        file.close()
        
        #parser1 = apache_log_parser.make_parser('%h %l %u %t "%r" %s %B')
        parser = apache_log_parser.make_parser(format_value)

        logs = []
        try:
            with open(log_data) as in_f:
                for line in in_f:
                    line = parser(line)
                    logs.append(line)
        except FileNotFoundError:
            print('Файл не был найден')
        
        
        for l in logs:
            ip = l['remote_host']
            logname = l['remote_logname']
            user = l['remote_user']
            date = l['time_received']
            date = date[1:-1]
            date_format = "%d/%b/%Y:%H:%M:%S %z"
            dt = datetime.strptime(date, date_format)
            request = l['request_first_line']
            status = l['status']
            bytes_sent = l['response_bytes']
            cursor.execute('''
                        INSERT INTO access_logs (ip, logname, user, date, request, status, bytes)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (ip, logname, user, dt, request, status, bytes_sent))
    
        conn.commit()
    
                

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
