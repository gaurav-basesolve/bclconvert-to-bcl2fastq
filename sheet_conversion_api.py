from flask import Flask, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from bcl_to_fastq import bcl_to_fastq
import os

# Creating dump dir with uploads, stage, downloads as subdirs
if not os.path.exists(f"{os.getcwd()}/dump"):
    os.mkdir(f"{os.getcwd()}/dump")
    os.mkdir(f"{os.getcwd()}/dump/uploads")
    os.mkdir(f"{os.getcwd()}/dump/downloads")
    os.mkdir(f"{os.getcwd()}/dump/stage")


UPLOAD_FOLDER = f'{os.getcwd()}/dump/uploads'
DOWNLOAD_FOLDER = f'{os.getcwd()}/dump/downloads'
ALLOWED_EXTENSIONS = {'txt', 'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            original_sample_sheet_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(original_sample_sheet_path)
        if request.form.get("reverse_compliment"):    
            if request.form.get("convert_download"):
                conv_filename = bcl_to_fastq(original_sample_sheet_path, True)
                return redirect(url_for('download_file', name=conv_filename))
        else:
            if request.form.get("convert_download"):
                conv_filename = bcl_to_fastq(original_sample_sheet_path)
                return redirect(url_for('download_file', name=conv_filename))
    
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <br></br>
      <input type="checkbox" name=reverse_compliment value="world" checked>
      <label for="reverse_compliment"> Check for reverse complement of index2 </label><br>
      <br></br>
      <button type=submit name=convert_download value=convert_download> Convert and Download </button>

    </form>
    '''


@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["DOWNLOAD_FOLDER"], name)

# run server
if __name__=="__main__":
    app.run(debug=True)

