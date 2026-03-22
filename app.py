# Nome: Caio Florentin de Oliveira | NUSP: 14562921
# SCC0251 - Processamento de Imagens

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import numpy as np
import base64
import imageio.v3 as iio
import photoshop 

app = Flask(__name__, static_folder='front', static_url_path='')
CORS(app)


@app.route('/')
def index():
    return send_from_directory('front', 'index.html')


@app.route('/process', methods=['POST'])
def process_image():
    try:
        data = request.json

        image_data = data.get('image')
        pipeline = data.get('pipeline', [])

        print(f"Recebido {len(pipeline)} transformações")
        for i, transform in enumerate(pipeline):
            print(f"  {i+1}. {transform['type']}: {transform['params']}")

        # Decodifica a imagem recebida em base64
        image_bytes = base64.b64decode(image_data.split(',')[1])
        img_array = iio.imread(image_bytes)
        # O front está passando como jpeg, que não tem canal alfa, mas o backend espera RGBA. Se vier RGBA, remove o canal alfa.
        print(img_array.shape)
        
        # Aplica cada transformação da pipeline
        all_warnings = []
        for transform in pipeline:
            transform_type = transform['type']
            params = transform['params']
            print(f"Aplicando transformação: {transform_type} com params {params}")
            new_img, step_warnings = photoshop.transform_image(img_array, transform_type, params)
            img_array = new_img
            all_warnings.extend(step_warnings)


        # Garante tipo uint8 antes de salvar
        img_array = np.clip(img_array, 0, 255).astype(np.uint8)

        iio.imwrite("debug_output.jpg", img_array)

        # Converte a imagem processada para bytes JPEG usando imageio
        jpeg_bytes = iio.imwrite("<bytes>", img_array, extension=".jpg")
        img_str = base64.b64encode(jpeg_bytes).decode()

        return jsonify({
            'success': True,
            'image': f'data:image/jpeg;base64,{img_str}',
            'warnings': all_warnings
        })

    except Exception as e:
        print(f"Erro no processamento: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500




if __name__ == '__main__':
    print("=" * 50)
    print("IMAGE EDITOR - Backend Flask")
    print("SCC0251 - Processamento de Imagens")
    print("=" * 50)
    print("\nServidor rodando em: http://localhost:5001")
    print("Pressione Ctrl+C para parar\n")
    app.run(debug=True, port=5001)