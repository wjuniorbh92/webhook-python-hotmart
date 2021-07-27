from flask import Flask, request, abort, jsonify
import psycopg2
import json
from flask_mail import Mail, Message
from emails import Email
from datetime import datetime

keyDatabase = [
    'id', 'transaction', 'payment_type', 'payment_engine', 'status', 'prod', 'prod_name', 'producer_name', 'producer_document', 'producer_legal_nature', 'purchase_date', 'confirmation_purchase_date', 'original_offer_price', 'productofferpaymentmode', 'warranty_date', 'installments_number', 'funnel', 'order_bump', 'price', 'email', 'name', 'signature_status', 'dataquery'
] # chose the fields in your Database

with open("config.json") as json_data_file:
    data = json.load(json_data_file)
# Update connection string information
host = data['sql']['host']
dbname = data['sql']['db']
user = data['sql']['user']
password = data['sql']['password']
port = data['sql']['port']

conn_string = "host={0} user={1} dbname={2} password={3} port={4}".format(
    host, user, dbname, password, port)
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

app = Flask(__name__)
mail = Mail(app)  # instantiate the mail class

# configuration of mail
app.config['MAIL_SERVER'] = data['mail']['mail-server']
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = data['mail']['username']
app.config['MAIL_PASSWORD'] = data['mail']['password']
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

def save_sql(rec: dict): #save all data in sql
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    cols = rec.keys()
    cols_str = ','.join(cols)
    vals = [rec[k] for k in cols]
    vals_str = ','.join(['%s' for i in range(len(vals))])
    sql_str = """INSERT INTO table ({}) VALUES ({})""".format(
        cols_str, vals_str)
    cursor.execute(sql_str, vals)
    cursor.execute("COMMIT")
    conn.close()

def canceled(jsonParse):  # this functions is when a webhook pass a canceled buy
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    sql = """UPDATE table
	    SET field-pay = 'false'
	    WHERE transaction = '{0}';""".format(jsonParse['transaction'])
    cursor.execute(sql)
    conn.commit()
    conn.close()
    msg = Message('Title for client', sender='user@email.com',
                  recipients=[jsonParse['email']])
    msg.html = Email.canceled(jsonParse['name'])
    mail.send(msg)
    return

def completed(jsonParse):
    msg = Message('Welcome User', sender='user@email.com',
                  recipients=[jsonParse['email']])
    msg.html = Email.aproved(
        jsonParse['name'], jsonParse['transaction'])
    mail.send(msg)
    return

def await_aproved(jsonParse):
    print("await_aproved")
    return

def aproved(jsonParse):
    print("aproved")
    # nada
    return

def refund(jsonParse):
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    sql = """UPDATE table
	    SET field=pay = 'false'
	    WHERE transaction = '{0}';""".format(jsonParse['transaction'])
    cursor.execute(sql)
    conn.commit()
    conn.close()
    msg = Message('Sorry!!!', sender='user@name.com',
                    recipients=[jsonParse['email']])
    msg.html = Email.canceled(jsonParse['name'])
    mail.send(msg)
    return


def chargeback(jsonParse):
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    sql = """UPDATE public.app_customuser
	    SET field=pay = 'false'
	    WHERE transaction = '{0}';""".format(jsonParse['transaction'])
    cursor.execute(sql)
    conn.commit()
    conn.close()
    msg = Message('Sorry!!!', sender='user@name.com',
                  recipients=[jsonParse['email']])
    msg.html = Email.canceled(jsonParse['name'])
    mail.send(msg)
    return

def dispute(jsonParse):
    print("dispute")
    # Query field=pay false
    return

def delay_payment(jsonParse):
    print("delay_payment")
    return

@app.route('/webhook', methods=['POST'])
def webhook():
    jsonParse = {}
    if request.method == 'POST':
        if request.form.get('hottok') == data['hotmart']['hottook']:
            jsonParse['dataquery'] = datetime.now().strftime(
                '%Y-%m-%d %H:%M:%S.%f')
            for key, val in request.form.items():
                if key in keyDatabase:
                    if len(val) == 0 or val == 'null' or val == None or val == '' or val == "NULL":
                        jsonParse[key] = '000'
                    else:
                        jsonParse[key] = val
                else:
                    pass
            save_sql(jsonParse) #save all data in SQL
            # this part test the status field and to a funcion
            if jsonParse['status'] == 'completed' or jsonParse['status'] == 'approved':
                completed(jsonParse)
            elif jsonParse['status'] == 'canceled':
                canceled(jsonParse)
            elif jsonParse['status'] == 'billet_printed':  # Aguardando Pagamento
                await_aproved(jsonParse)
            elif jsonParse['status'] == 'refunded':  # Compra Reembolsada
                refund(jsonParse)
            elif jsonParse['status'] == 'chargeback':  # chargeback extorno no cartão
                chargeback(jsonParse)
            elif jsonParse['status'] == 'dispute':  # Reembolsada
                dispute(jsonParse)
            elif jsonParse['status'] == 'expired' or jsonParse['status'] == 'delayed':
                delay_payment(jsonParse)
            return 'success', 200
        else:
            return 'denied',401
    else:
        abort(400)


# if __name__ == '__main__':
#     app.run(host='0.0.0.0')
