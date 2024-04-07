from reactpy import component, html, run
from reactpy.backend.fastapi import configure
from fastapi import FastAPI, UploadFile
from fastapi.responses import Response 

import qrcode
import qrcode.image.svg

app = FastAPI()

@app.get('/qrcode')
async def get_qrcode():
    url = 'http://127.0.0.1:8000'
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
            dst_file = f'C:/Users/xu_q2/Downloads/{file.filename}'
            with open(dst_file, 'wb') as f:
                while contents := file.file.read(1024 * 1024):
                    f.write(contents)
        except Exception:
            return {'message': 'There was an error uploading the file(s)'}
        finally:
            file.file.close()
    return {'message': f'Successfuly uploaded {[file.filename for file in files]}'} 

@component
def HelloWorld():
    return html.div(
        html.h3('上传文件：'),
        html.form(
            {'action': '/upload', 'enctype': 'multipart/form-data', 'method': 'post'},
            html.input({'name': 'files', 'type': 'file', 'multiple': True}),
            html.input({'type': 'submit'}),
        ),
        html.h3('扫码访问服务器：'),
        html.img({'src': '/qrcode', 'alt': 'qrcode not display', 'style': {'height': '200px'}}),
    )

configure(app, HelloWorld)