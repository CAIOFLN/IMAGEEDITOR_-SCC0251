# Gera imagens de comparação (original vs resultado) para o relatório
# Uso: python3 generate_comparison.py <imagem> <transform_type> [param=valor ...]
#
# Exemplos:
#   python3 generate_comparison.py foto.jpg gamma gamma=0.5
#   python3 generate_comparison.py foto.jpg rotation angle=45
#   python3 generate_comparison.py foto.jpg contrast a=50 b=200 c=0 d=255
#   python3 generate_comparison.py foto.jpg translation dx=50 dy=30
#   python3 generate_comparison.py foto.jpg creative L=100
#   python3 generate_comparison.py foto.jpg scale sx=1.5 sy=1.5

import sys
import imageio.v3 as iio
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import photoshop

TRANSFORM_LABELS = {
    'translation': 'Translação',
    'rotation':    'Rotação',
    'scale':       'Escala',
    'inverse':     'Inversa',
    'log':         'Log',
    'gamma':       'Gama',
    'contrast':    'Contraste',
    'creative':    'Limiar (Threshold)',
}

def parse_params(args):
    params = {}
    for arg in args:
        key, val = arg.split('=')
        try:
            params[key] = int(val)
        except ValueError:
            params[key] = float(val)
    return params

def param_str(transform_type, params):
    if not params:
        return ''
    if transform_type == 'gamma':
        return f"γ = {params.get('gamma')}"
    if transform_type == 'rotation':
        return f"ângulo = {params.get('angle')}°"
    if transform_type == 'translation':
        return f"dx = {params.get('dx')}, dy = {params.get('dy')}"
    if transform_type == 'scale':
        return f"sx = {params.get('sx')}, sy = {params.get('sy')}"
    if transform_type == 'contrast':
        return f"a={params.get('a')}, b={params.get('b')}, c={params.get('c')}, d={params.get('d')}"
    if transform_type == 'creative':
        return f"L = {params.get('L')}"
    return ', '.join(f'{k}={v}' for k, v in params.items())

def main():
    if len(sys.argv) < 3:
        print("Uso: python3 generate_comparison.py <imagem> <transform_type> [param=valor ...]")
        sys.exit(1)

    image_path = sys.argv[1]
    transform_type = sys.argv[2]
    params = parse_params(sys.argv[3:])

    img = iio.imread(image_path)
    if img.ndim == 2:
        img = np.stack([img] * 3, axis=-1)
    elif img.shape[2] == 4:
        img = img[:, :, :3]

    result, warnings = photoshop.transform_image(img, transform_type, params)

    label = TRANSFORM_LABELS.get(transform_type, transform_type)
    pstr  = param_str(transform_type, params)
    title = label if not pstr else f"{label}  —  {pstr}"

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle(title, fontsize=14, fontweight='bold', y=1.02)

    axes[0].imshow(img)
    axes[0].set_title('Original', fontsize=11)
    axes[0].axis('off')

    axes[1].imshow(result)
    axes[1].set_title('Resultado', fontsize=11)
    axes[1].axis('off')

    if warnings:
        fig.text(0.5, -0.02, ' | '.join(warnings), ha='center',
                 fontsize=8, color='orange', wrap=True)

    fig.tight_layout()

    out_dir = Path('comparisons')
    out_dir.mkdir(exist_ok=True)
    pstr_file = pstr.replace(' ', '').replace(',', '_').replace('=', '')
    out_file = out_dir / f"{transform_type}_{pstr_file}.png"
    fig.savefig(out_file, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"Salvo em: {out_file}")

if __name__ == '__main__':
    main()
