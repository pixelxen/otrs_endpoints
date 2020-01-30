#!/usr/bin/python

from flask import Flask
from flask import jsonify
from flask import request
import subprocess as sp
import os

app = Flask(__name__)

otrs_uid = 1008
otrs_gid = 1008

# Change gid in subprocess
def demote(user_uid, user_gid):
    """Pass the function 'set_ids' to preexec_fn, rather than just calling
    setuid and setgid. This will change the ids for that subprocess only"""
    def set_ids():
        os.setgid(user_gid)
        os.setuid(user_uid)
    return set_ids

def launch_command(bash_command):
    p = sp.Popen(
            bash_command,
            stdout=sp.PIPE,
            stderr=sp.PIPE,
            preexec_fn=demote(otrs_uid, otrs_gid)
            )
    output, error = p.communicate()
    if p.returncode == 0:
        response = {
                'result': 'success',
                'message': output,
                'command': bash_command
                }
    else:
        response = {
                'result': 'error',
                'message': output + error,
                'command': bash_command,
                'exit_code': p.returncode
                }
    return response

# Add company
@app.route('/api/v1/Admin/CustomerCompany/Add', methods=['GET'])
def admin_customercompany_add():
    customer_id = request.args.get('customer_id', default = None, type = str)
    name        = request.args.get('name',        default = None, type = str)

    # default response is error
    response = {'result': 'error'}
    if customer_id is None:
        response['message'] = "No 'customer_id' given"
    elif name is None:
        response['message'] = "No 'name' given"
    else:
        bash_command = [
                "/opt/otrs/bin/otrs.Console.pl",
                "Admin::CustomerCompany::Add",
                "--customer-id", customer_id,
                "--name",        name
                ]
        response = launch_command(bash_command)
        print response['message']
    return jsonify(response)


# Add user
@app.route('/api/v1/Admin/CustomerUser/Add', methods=['GET'])
def admin_customeruser_add():
    user_name     = request.args.get('user_name',     default = None, type = str)
    first_name    = request.args.get('first_name',    default = None, type = str)
    last_name     = request.args.get('last_name',     default = None, type = str)
    email_address = request.args.get('email_address', default = None, type = str)
    customer_id   = request.args.get('customer_id',   default = None, type = str)

    # default response is error
    response = {'result': 'error'}
    if user_name is None:
        response['message'] = "No 'user_name' given"
    elif first_name is None:
        response['message'] = "No 'first_name' given"
    elif last_name is None:
        response['message'] = "No 'last_name' given"
    elif email_address is None:
        response['message'] = "No 'email_address' given"
    elif customer_id is None:
        response['message'] = "No 'customer_id' given"
    else:
        bash_command = [
                "/opt/otrs/bin/otrs.Console.pl",
                "Admin::CustomerUser::Add",
                "--user-name",     user_name,
                "--first-name",    first_name,
                "--last-name",     last_name,
                "--email-address", email_address,
                "--customer-id",   customer_id
                ]
        response = launch_command(bash_command)
        print response['message']
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
