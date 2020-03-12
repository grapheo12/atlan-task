"""
REST APIs for query/upload on CSV data file.
"""
import csv
import datetime
import os
import time

import dotenv
from flask import Flask, request
from flask_restplus import Api, Resource, reqparse, abort, fields
import werkzeug

from app.threadManager import ThreadManager

dotenv.load_dotenv(".env")

app = Flask(__name__)
api = Api(app)
tm = ThreadManager()

#Required for query
app.config["DATA_URL"] = os.environ.get("DATA_URL")
app.config["UPLOAD_PATH"] = os.environ.get("UPLOAD_PATH")

#File parser
#Taken from https://stackoverflow.com/questions/40547670/python-restplus-api-to-upload-and-dowload-files
file_upload = reqparse.RequestParser()
file_upload.add_argument("csv",
                        type=werkzeug.datastructures.FileStorage,
                        location='files',
                        required=True,
                        help="CSV File")
file_upload.add_argument("ticket",
                        type=str,
                        required=True,
                        help="Run a GET request to get a upload ticket")

class Data:
    lines_read: int = 0
    complete: bool = False

@tm.pausableTask(Data)
def fileUploadHandler(*args, **kwargs):
    ref = args[0]
    ref.output.lines_read = 0
    ref.output.complete = False
    f = open(ref.args[1], "wb")
    try:
        while True:
            assert ref.status == "RUN"
            f.write(ref.args[0].readline())
            time.sleep(0.5)    #Artificial delay for demo
    except:
        f.close()
        if ref.status == "TERM":
            os.remove(ref.args[1])
        ref.args[0].close()
        ref.output.complete = True

class TicketMixin:
    def get(self):
        return str(datetime.datetime.now())

    @api.doc(params={"ticket": "Upload ticket"})
    def delete(self):
        ticket = request.args.get("ticket")
        tm.refs[ticket].terminate()
        return "Terminated"

@api.route("/upload")
class FileUploader(TicketMixin, Resource):
    @api.expect(file_upload)
    def post(self):
        args = file_upload.parse_args()
        if args['csv'].mimetype == "text/csv":
            fileName = f"{app.config['UPLOAD_PATH']}/{args['ticket']}.csv"
            fu = fileUploadHandler(args['ticket'], args['csv'].stream, fileName)
            fu.start()
        else:
            abort(404)
        print(fu.output.__dict__)
        while not fu.output.complete:
            pass

        if fu.status != "TERM":
            fu.terminate()

        return {"success": "Upload complete"}

@tm.pausableTask(Data)
def exportHandler(*args, **kwargs):
    ref = args[0]
    ref.output.lines_read = 0
    ref.output.complete = False
    ref.output.lines = []
    row = ref.args[0]

    f = open(app.config["DATA_URL"], "r")
    for line in csv.reader(f):
        if ref.status == "RUN" and row > 0:
            row -= 1
            ref.output.lines.append(line)
            time.sleep(0.5)   #Artificial delay for demo
        else:
            if ref.status != "RUN":
                ref.output.lines = []    #Freeing up memory
            ref.output.complete = True
            break
    f.close() 

@api.route("/export")
class RowExporter(TicketMixin, Resource):
    @api.expect(api.model('Query', {
        "rows": fields.Integer,
        "ticket": fields.String
    }))
    def post(self):
        req = request.json
        row = int(req['rows'])

        ex = exportHandler(req['ticket'], row)
        ex.start()

        while not ex.output.complete:
            pass

        if ex.status != "TERM":
            ex.terminate()

        return {"rows": ex.output.lines}
