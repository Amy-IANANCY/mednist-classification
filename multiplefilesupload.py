import shutil, os
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
import pandas as pd


from inference import get_prediction

app = Flask(__name__)

app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

#Creation of dedicated folders for each class
path = os.getcwd()
ABDOMEN_FOLDER = os.path.join(path, 'abdomen')
app.config['ABDOMEN_FOLDER'] = ABDOMEN_FOLDER

BREAST_FOLDER = os.path.join(path, 'breast')
app.config['BREAST_FOLDER'] = BREAST_FOLDER

CHEST_FOLDER = os.path.join(path, 'chest')
app.config['CHEST_FOLDER'] = CHEST_FOLDER

CRX_FOLDER = os.path.join(path, 'crx')
app.config['CRX_FOLDER'] = CRX_FOLDER

HAND_FOLDER = os.path.join(path, 'hand')
app.config['HAND_FOLDER'] = HAND_FOLDER

HEAD_FOLDER = os.path.join(path, 'head')
app.config['HEAD_FOLDER'] = HEAD_FOLDER


folder_dict = {"0": ABDOMEN_FOLDER,
               "1": BREAST_FOLDER,
               "2": CHEST_FOLDER,
               "3": CRX_FOLDER,
               "4": HAND_FOLDER,
               "5": HEAD_FOLDER}


# Make directory if dedicated folder not exists
for folder in folder_dict.values():
    if not os.path.isdir(folder):
        os.mkdir(folder)

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'files[]' not in request.files:
            flash('No file part')
            return redirect(request.url)

        files = request.files.getlist('files[]')

        abdo_list = []
        breast_list = []
        chest_list = []
        crx_list = []
        hand_list = []
        head_list = []

        files_list = [abdo_list, breast_list, chest_list, crx_list, hand_list, head_list]
        titles = ['Abdomen', 'Breast', 'Chest', 'CRX', 'Hand', 'Head']

        for file in files:
            if file and allowed_file(file.filename):
                print(file.filename)
                img_bytes = file.read()
                class_name, class_id = get_prediction(image_bytes=img_bytes)
                print("class_name = {}, class_id = {}".format(class_name, class_id))


                class_name = str(class_name)
                class_id = str(class_id)

                filename = secure_filename(file.filename)

                if class_name in folder_dict.keys():
                    file.save(os.path.join(folder_dict[class_name], filename))
                    index = int(class_name)
                    files_list[index].append(filename)
                else:
                    file.save(os.path.join(folder_dict[class_id], filename))
                    index = int(class_id)
                    files_list[index].append(filename)

        data = zip(titles, files_list)

        for fold in folder_dict.values():
            for filename in os.listdir(fold):
                file_path = os.path.join(fold, filename)
                os.unlink(file_path)

        return render_template('result_folder.html',
                               data=data)
                               #folder_title=titles)

    return render_template('index.html')






        #flash('File(s) successfully uploaded')
        #return redirect('/')

        # TODO: bouton retour et empty folders

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=int(os.environ.get('PORT', 5000)), debug=True, threaded=True)

