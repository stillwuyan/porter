from reactpy import component, html, run, event, use_state
from reactpy.backend.fastapi import configure
from fastapi import FastAPI, UploadFile
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
import uvicorn
import qrcode
import qrcode.image.svg
import socket
import pathlib

download_path = 'C:/Users/sizzle/Downloads'
download_uri = '/static/'

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    s.connect(('114.114.114.114', 53))
    return s.getsockname()[0]

app = FastAPI()

@app.get('/qrcode')
async def get_qrcode():
    url = f'http://{get_ip_address()}:8000'
    qr = qrcode.QRCode(
        image_factory=qrcode.image.svg.SvgPathImage,
        box_size=20,
        border=1)
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image()
    return Response(content=img.to_string(encoding='utf-8'), media_type='image/svg+xml')

@app.post('/upload')
async def upload(files: list[UploadFile]):
    for file in files:
        try:
            dst_file = f'{download_path}/{file.filename}'
            with open(dst_file, 'wb') as f:
                while contents := file.file.read(1024 * 1024):
                    f.write(contents)
        except Exception:
            return {'message': 'There was an error uploading the file(s)'}
        finally:
            file.file.close()
    return {'message': f'Successfuly uploaded {[file.filename for file in files]}'} 

@app.get('download')
async def download():
    pass

app.mount('/static', StaticFiles(directory=download_path), name='static')
message = ''

# Front End
@component
def index():
    @event(prevent_default=True)
    def handle_clipboard(event):
        global message
        message = event['target']['value']

    vertical_align_style = {
    }

    return html.div(
        html.style('''
            .vertical-align {
                display: flex;
                flex-direction: column;
                align-items: flex-start;
            }
            textarea {
                width: 252px;
                border: 1px solid #EEE
            }
            .input_container {
                border: 1px solid #E5E5E5;
            }
            input[type=file]::file-selector-button {
                background-color: #EEE;
                color: #000;
                border: 1px;
                border-right: 1px solid #E5E5E5;
                padding: 10px 10px;
                margin-right: 10px;
                width: 80px;
            }
            input[type=file]::file-selector-button:hover {
                background-color: #CCC;
                border: 0px;
                border-right: 1px solid #E5E5E5;
            }
            input[type=submit] {
                background-color: #EEE;
                color: #000;
                border: 1px;
                border-right: 1px solid #E5E5E5;
                padding: 10px 10px;
                width: 80px;
                margin-top: 5px;
            }
            input[type=submit]:hover {
                background-color: #CCC;
                border: 0px;
                border-right: 1px solid #e5e5e5;
            }
            p {
                margin: 0px;
                padding: 5px;
                border: 1px solid #e5e5e5;
            }
        '''),
        html.h3('剪贴板：'),
        html.div(
            {'class_name': 'vertical-align'},
            html.textarea({
                'name': 'clipboard',
                'rows': '3',
                'on_change': handle_clipboard,
                'value': message
            }),
        ),
        html.h3('上传文件：'),
        html.form(
            {
                'class_name': 'vertical-align',
                'action': '/upload',
                'method': 'post',
                'enctype': 'multipart/form-data'
            },
            html.div(
                {'class_name': 'input_container'},
                html.input({'name': 'files', 'type': 'file', 'multiple': True})
            ),
            html.input({'type': 'submit'}),
        ),
        html.h3('下载文件：'),
        html.div(
            {'class_name': 'vertical-align'},
            [html.a({'href': f'{download_uri}{file.name}'}, f'{file.name}') for file in pathlib.Path(download_path).glob('*')],
        ),
        html.h3('扫码访问服务器：'),
        html.div(
            {'class_name': 'vertical-align'},
            html.p(f'URL: http://{get_ip_address()}:8000'),
            html.img({'src': '/qrcode', 'alt': 'qrcode not display'}),
        )
    )

if __name__ == '__main__':
    configure(app, index)
    uvicorn.run(app, host='0.0.0.0', port=8000)
