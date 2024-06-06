from reactpy import component, html, run, event, use_state
from reactpy.backend.fastapi import configure
from fastapi import FastAPI, UploadFile
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
import uvicorn

import qrcode
import qrcode.image.svg

import socket

download_path = 'C:/Users/xu_q2/Downloads'
download_file = '/static/1.jpg'

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

app.mount('/static', StaticFiles(directory='static', html=True), name='static')
message = ''
# Front End
@component
def index():
    global message
    @event(prevent_default=True)
    def handle_clipboard(event):
        global message
        message = event['target']['value']

    vertical_align_style = {
        'display': 'flex',
        'flex-direction': 'column',
        'align-items': 'flex-start',
    }
    print(f'render index, message: {message}')
    return html.div(
        {'style': vertical_align_style},
        html.h3('剪贴板：'),
        html.form(
            {'action': '/clipboard', 'method': 'post', 'style': vertical_align_style},
            html.textarea({'name': 'clipboard', 'rows': '3', 'cols': 25, 'on_change': handle_clipboard, 'value': message}),
        ),
        html.h3('上传文件：'),
        html.form(
            {'action': '/upload', 'method': 'post', 'enctype': 'multipart/form-data', 'style': vertical_align_style},
            html.input({'name': 'files', 'type': 'file', 'multiple': True}),
            html.input({'type': 'submit'}),
        ),
        html.h3('下载文件：'),
        html.a({'href': f'{download_file}'}, f'http://{get_ip_address()}:8000{download_file}'),
        html.h3('扫码访问服务器：'),
        html.input({'type': 'text', 'readonly': True, 'value': f'http://{get_ip_address()}:8000'}),
        html.img({'src': '/qrcode', 'alt': 'qrcode not display', 'style': {'height': '200px'}}),
    )

if __name__ == '__main__':
    configure(app, index)
    uvicorn.run(app, host='0.0.0.0', port=8000)
