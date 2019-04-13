# Upload multiple images and prpocess flc

import glob
import os, shutil
import flc
import time
import zipfile
import jsonpickle, ConfigParser
from flask import Flask, request, Response
from gevent import wsgi
from werkzeug.utils import secure_filename

# Initialize the Flask application
app = Flask(__name__)

config = ConfigParser.ConfigParser()
config.read('flc.conf')
root_folder = config.get('input_path', 'root_folder')
test_data_dir = root_folder + '/test_data'
cwd = test_data_dir + '/1_images'
subdir_list = None
ALLOWED_EXTENSIONS = {'zip'}

print("Flc server started")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Route http posts to this method
@app.route('/api/image', methods=['POST'])
def upload_image():
    try:
        os.chdir(cwd)
        start = time.time()
        print('Uploading the file ... Wait !!!\n')

        # Upload multiple images
        if request.method == 'POST' and 'image' in request.files:
            for file in request.files.getlist('image'):
                file.save(file.filename)
                print('Uploaded tea image - ', file.filename, '\n')

        # Upload single image
        # file = request.files['image']
        # file.save(file.filename)
        # print('Uploaded - ', file.filename, '\n')
        end = time.time()
        print('leaf image upload time = ', round((end - start), 2), ' seconds')
        responses = {'tea_image_uploaded': file.filename
                     }
        response_pickled = jsonpickle.encode(responses)
        return Response(response=response_pickled, status=200, mimetype="application/json")
    except Exception as e:
        return str(e)


@app.route('/api/flc', methods=['POST'])
def classification_flc_only():
    try:
        start = time.time()
        cc, fc = flc.flc_only()
        end = time.time()
        time_cons = (end - start)
        print('classification time = ', round(time_cons, 2), ' seconds')
        responses = {'Fine_Count': fc,
                     'Coarse_Count': cc,
                     'Time Taken(seconds)': round(time_cons, 2)
                     }
        response_pickled = jsonpickle.encode(responses)
        return Response(response=response_pickled, status=200, mimetype="application/json")
    except:
        try:
            p = os.listdir(test_data_dir)
            length = len(p)

            def alldell(a):
                for root, dirs, files in os.walk(a):
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))

            for i in xrange(length):
                path = test_data_dir + '/' + p[i]
                alldell(path)
            responses = {'status': 'Error_Try_Again'
                         }
            response_pickled = jsonpickle.encode(responses)
            return Response(response=response_pickled, status=200, mimetype="application/json")
        except Exception as e:
            return str(e)


@app.route('/api/bigdata', methods=['POST'])
def upload_big_data():
    os.chdir(cwd)
    start = time.time()
    if request.method == 'POST':
        # print('\nUploading the file ... Wait !!!')
        file = request.files['bigData']
        print('1')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(cwd, filename))
            zip_ref = zipfile.ZipFile(os.path.join(cwd, filename), 'r')
            zip_ref.extractall(cwd)
            zip_ref.close()
            r = glob.glob(cwd + '/*.zip')
            for i in sorted(r):
                os.remove(i)
            for x, y, z in os.walk(cwd):
                subdir_list = y
                break
            for each in subdir_list:
                os.system('mv ' + cwd + '/' + each + '/* ' + cwd)
                os.system('rm -r ' + cwd + '/' + each)
    end = time.time()
    time_cons = (end - start)
    image_count = len([name for name in os.listdir(cwd) if os.path.isfile(os.path.join(cwd, name))])
    print('Uploaded - ', file.filename)
    print('Time_Taken(seconds) - ', round(time_cons, 2))
    print('Total images - ', image_count)
    responses = {'Uploaded': file.filename,
                 'image_counts': image_count,
                 'Time_Taken(seconds)': round(time_cons, 2)
                 }
    response_pickled = jsonpickle.encode(responses)
    return Response(response=response_pickled, status=200, mimetype="application/json")


@app.route('/api/cleandir', methods=['POST'])
def post():
    try:
        p = os.listdir(test_data_dir)
        length = len(p)

        def alldell(a):
            for root, dirs, files in os.walk(a):
                for f in files:
                    os.unlink(os.path.join(root, f))
                for d in dirs:
                    shutil.rmtree(os.path.join(root, d))

        for i in xrange(length):
            path = test_data_dir + '/' + p[i]
            alldell(path)
        responses = {'status': 'deleted'
                     }
        response_pickled = jsonpickle.encode(responses)
        return Response(response=response_pickled, status=200, mimetype="application/json")

    except Exception as e:
        return str(e)


# start flask app
# app.run(host="0.0.0.0", port=5000)  # Server
# app.run(port=6000)  # Local

server = wsgi.WSGIServer(('127.0.0.1', 5000), app)
server.serve_forever()
