import socket
from flask import Flask, render_template,request,jsonify 

ADDRESS = 'localhost'
PORT = 1234

app=Flask(__name__)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
sock.connect((ADDRESS, PORT))

@app.route('/')
def principal():
    return render_template('index.html')

@app.route('/actualizar_estado', methods=['POST'])
def actualizar_estado():
    #sock.send(b"L1")
    data = request.json
    dispositivo = data.get('dispositivo')
    estado = data.get('estado')
    print(f'Dispositivo: {dispositivo}, Estado: {estado}')
    command = dispositivo+estado
    print(f"Sending through sock: {command}")
    sock.send(command.encode('utf-8'))
    return jsonify({'message': 'Estado actualizado'}), 200




if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0',debug=True,port=5017)#se reinicia el servidor automaticamente
    except KeyboardInterrupt:
        sock.close()

        


