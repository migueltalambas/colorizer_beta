# from msilib.schema import File
# from urllib import response
# from flask import Flask, Response, render_template, request
# from colorizer import Colorizer

# app = Flask(__name__)
# colorizer = Colorizer

# @app.route('/')
# def home():
#     return render_template('index.html')

# @app.route('/submit', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         file = request.files['file']
#         print(file.filename)
#         return render_template('index.html')
#     else:
#         return render_template('index.html')


# @app.route('/display',methods=['GET', 'POST'] )
# def run():
#     if request.method == 'POST':
#         colorizer.processImage(response())
#         return render_template('display.html')

# if __name__ == '__main__':
#     app.run(debug=True, port=4545)

from re import X
from urllib import response
from cv2 import filterHomographyDecompByVisibleRefpoints
from flask import Flask, Response, render_template, request, flash, redirect, url_for, send_from_directory
#from colorizer import Colorizer
from werkzeug.utils import secure_filename
from colorizer import Colorizer
import os


UPLOAD_FOLDER_IMAGE = 'uploads_im'
UPLOAD_FOLDER_VIDEO = 'uploads_vi'

ALLOWED_EXTENSIONS_P = {'txt', 'pdf', 'png','jfif', 'jpg', 'jpeg', 'gif'}
ALLOWED_EXTENSIONS_V = {'mp4', 'avi'} #

app = Flask(__name__)
app.config['UPLOAD_FOLDER_IMAGE'] = UPLOAD_FOLDER_IMAGE
app.config['UPLOAD_FOLDER_VIDEO'] = UPLOAD_FOLDER_VIDEO


def colorize_func(img):
    colorizer = Colorizer(use_cuda=True, width = 640, height = 480)
    return colorizer.processImage(img)

def colorize_video(video):
    colorizer = Colorizer(use_cuda=True, width = 640, height = 480)
    return colorizer.processVideo(video)


def allowed_file_p(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_P

def allowed_file_v(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_V


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file_p(file.filename):
            
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGE'], filename))
            return redirect(url_for('uploaded_image',
                                    filename=filename))

        if file and allowed_file_v(file.filename):

            print(file)
            filename = secure_filename(file.filename)
            print(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER_VIDEO'], filename))
            return redirect(url_for('uploaded_video',
                                    filename=filename))

    return render_template('index.html')


@app.route('/uploads_im/<filename>')
## color images (button colorize)
def uploaded_image(filename):
    #print('first ', filename)
    path = "uploads_im/"
    full = path + filename
    col = colorize_func(full)
    print('IMAGE COLORIZATION')
    #print('second ', col)
    return send_from_directory('output/', filename)

@app.route('/uploads_vi/<filename>')
def uploaded_video(filename):
    path = "uploads_vi/"
    full = path + filename
    print('VIDEO COLORIZATIONNN')
    col_vid = colorize_video(full)
    #print('third', col_vid)
    #return send_from_directory('output/', filename)~
    return send_from_directory('output/', filename)

# @app.route('/', methods=['GET', 'POST'])
# #upload video
# def upload_file_video():
#     if request.method == 'POST':
#         # check if the post request has the file part
#         if 'file_video' not in request.files:
#             flash('No file part')
#             return redirect(request.url)
#         file = request.files['file_video']
#         # if user does not select file, browser also
#         # submit an empty part without filename
#         if file.filename == '':
#             flash('No selected file')
#             return redirect(request.url)
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#             return redirect(url_for('uploaded_file',
#                                     filename=filename))
#     print('VIDEO')
            
#     return render_template('index.html')
    

if __name__ == '__main__':
    app.run(debug=True, port=4545)