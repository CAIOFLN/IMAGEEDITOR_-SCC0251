# Nome: Caio Florentin de Oliveira | NUSP: 14562921
# Curso: SCC0251 - Processamento de Imagens
# Ano/Semestre: 2026/1
# Trabalho 01: meu primeiro Software Genérico de Edição de Imagens
#
# Descrição: Este módulo implementa todas as transformações de imagem do editor.
# A função de entrada é transform_image(), chamada pelo servidor Flask (app.py).
# Transformações geométricas usam mapeamento inverso com matrizes homogêneas 3x3.
# Transformações de intensidade operam diretamente sobre os valores dos pixels.


import imageio.v3 as iio
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from pathlib import Path


# --- Matrizes inversas para mapeamento inverso ---
# No mapeamento inverso, percorremos a imagem de saída e, para cada pixel (x,y),
# aplicamos M^{-1} para encontrar a posição de origem (x', y') na imagem original.

def inv_translation_matrix(ti, tj):
    # Matriz inversa de translação: desloca (x,y) de volta em (-ti, -tj)
    return np.array([[1, 0, -ti],
            [0, 1, -tj],
            [0, 0, 1]])

def inv_rot_matrix(theta):
    # Matriz inversa de rotação por ângulo theta (transposta da matriz direta)
    return np.array([[np.cos(theta), np.sin(theta), 0],
            [-np.sin(theta), np.cos(theta), 0],
            [0, 0, 1]])

def inv_scale_matrix(si, sj):
    # Matriz inversa de escala: divide as coordenadas pelos fatores de escala
    return np.array([[1.0 / si, 0, 0],
            [0, 1.0 / sj, 0],
            [0, 0, 1]] )

# --- Transformações de Intensidade ---
# Cada função opera pixel a pixel sobre os valores de intensidade (0–255).
# Os três canais RGB são processados de forma independente, exceto em f_threshold.

def f_inv(light):
    # Inversão: f(x) = 255 - x  
    return 255-light

def f_log(light):
    # Compressão logarítmica: f(x) = log(x+1) / log(256) * 255
    img = np.log(light.astype(float)+1)
    img = img * 255/np.log(255+1)
    return img.astype(np.uint8)

def f_gamma(light, gamma=2.2):
    # Correção de gama: f(x) = x^(1/γ) * 255 / 255^(1/γ)
    img = light.astype(float)**(1/gamma)
    img = img * 255/(255**(1/gamma))
    return img.astype(np.uint8)

def f_threshold(img, L=128):
    # Limiarização criativa: mantém pixels com luminância > L, zera os demais
    gray = (0.299 * img[:, :, 0] + 0.587 * img[:, :, 1] + 0.114 * img[:, :, 2])
    mask = (gray > L)[:, :, np.newaxis]
    return np.where(mask, img, 0).astype(np.uint8)


## Salva a imagem  da função de modulação de contraste na pasta debug_curves para análise posterior
def save_f_mod_curve(a, b, c, d):
    # Create an array for input values (0 to 255)
    x = np.arange(256, dtype=float)
    # Initialize an array to store the output (y values)
    y = np.zeros_like(x)
    # Apply the piecewise transformation:
    # For x < a: linear from (0, 0) to (a, c)
    y[x < a] = x[x < a] * (c / a)
    # For a <= x < b: linear from (a, c) to (b, d)
    y[(x >= a) & (x < b)] = ((x[(x >= a) & (x < b)] - a) * ((d - c) / (b - a)) + c)
    # For x >= b: linear from (b, d) to (255, 255)
    y[x >= b] = ((x[x >= b] - b) * (255 - d) / (255 - b)) + d
    # Define output directory and file path
    output_dir = Path(__file__).resolve().parent / "debug_curves"
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    output_file = output_dir / f"f_mod_a{a}_b{b}_c{c}_d{d}_{timestamp}.png"

    # Plot the transformation curve
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(x, y, color='tab:blue', linewidth=2, label='f_mod(x)')
    ax.set_title(f"Contrast modulation: a={a}, b={b}, c={c}, d={d}")
    ax.set_xlabel("Input intensity")
    ax.set_ylabel("Output intensity")
    ax.set_xlim(0, 255)
    ax.set_ylim(0, 255)
    ax.grid(alpha=0.3)
    ax.legend(loc='best')

    # Save the plot and close the figure
    fig.tight_layout()
    fig.savefig(output_file, dpi=120)
    plt.close(fig)

    # Print the save location
    print(f"Curva f_mod salva em: {output_file}")

def f_mod(img, a=30, b=200, c=0, d=255):
    # Modulação de contraste com transformação linear por partes.
    # Três segmentos lineares definidos por quatro pontos de controle (a, b, c, d):
    #   [0, a]   → [0, c]      (segmento de sombras)
    #   [a, b]   → [c, d]      (segmento de meios-tons — onde o contraste é ajustado)
    #   [b, 255] → [d, 255]    (segmento de realces)
    try:
        img_float = img.astype(float)
        # For z < a, the transformation is linear from (0, 0) to (a, c)
        img_float[img_float < a] = img_float[img_float < a] * (c / a)
        # For a <= z < b, the transformation is linear from (a, c) to (b, d)
        img_float[(img_float >= a) & (img_float < b)] = ((img_float[(img_float >= a) & (img_float < b)] - a) * ((d - c) / (b - a)) + c)
        # For z >= b, the transformation is linear from (b, d) to (255, 255)
        img_float[img_float >= b] = ((img_float[img_float >= b] - b) * (255 - d) / (255 - b)) + d
        save_f_mod_curve(a, b, c, d)
        return np.clip(img_float, 0, 255).astype(np.uint8)
    
    except Exception as error:
        print(f"Error during function application: {error}")
        return img
    




# --- Transformações Geométricas ---
# Todas usam mapeamento inverso: para cada pixel (x,y) da saída, aplica-se
# a matriz M^{-1} para encontrar (x', y') na imagem original.
# Se (x', y') cair fora dos limites, aplica-se border clamping (replica borda),
# evitando pixels vazios conforme exigido pelo enunciado.

def apply_translation(img, new_img, dx, dy):
    # Desloca a imagem (dx, dy) pixels. A matriz inversa subtrai o deslocamento,
    # buscando o pixel de origem em (x - dx, y - dy).
    print(f"Aplicando translação: dx={dx}, dy={dy}")
    print(f"Imagem shape: {img.shape}")
    h, w, _ = img.shape
    m = inv_translation_matrix(dx, dy)
    clamped = False
    for i in range(h):
        for j in range(w):
            p = np.array([j, i, 1])
            p_new = m @ p

            x_new = int(p_new[0])
            y_new = int(p_new[1])

            # Avisa se o pixel de origem está fora dos limites da imagem original, mas aplica clamping para evitar pixels vazios
            if not (0 <= x_new < w and 0 <= y_new < h):
                clamped = True
            x_src = np.clip(x_new, 0, w - 1)
            y_src = np.clip(y_new, 0, h - 1)
            new_img[i, j] = img[y_src, x_src]
    return new_img, clamped

def apply_rotation(img, new_img, theta):
    # Rotaciona a imagem em torno do seu centro geométrico (cx, cy).
    # A matriz composta é: T^{-1}(-cx,-cy) @ R^{-1}(theta) @ T^{-1}(cx,cy)
    print(f"Aplicando rotação: theta={theta} radianos")
    print(f"Imagem shape: {img.shape}")
    h, w, _ = img.shape

    cx = (w) / 2
    cy = (h) / 2
    m = inv_translation_matrix(-cx, -cy) @ inv_rot_matrix(theta) @ inv_translation_matrix(cx, cy)

    clamped = False
    for i in range(h):
        for j in range(w):
            p = np.array([j, i, 1])
            p_new = m @ p

            x_new = int(p_new[0])
            y_new = int(p_new[1])
            # Avisa se o pixel de origem está fora dos limites da imagem original, mas aplica clamping para evitar pixels vazios

            if not (0 <= x_new < w and 0 <= y_new < h):
                clamped = True
            x_src = np.clip(x_new, 0, w - 1)
            y_src = np.clip(y_new, 0, h - 1)
            new_img[i, j] = img[y_src, x_src]
    return new_img, clamped

def apply_scale(img, new_img, sx, sy):
    # Redimensiona a imagem em relação ao centro geométrico (cx, cy).
    # A matriz composta é: T^{-1}(-cx,-cy) @ S^{-1}(sx,sy) @ T^{-1}(cx,cy)
    # sx, sy < 1 → afasta (bordas aparecem); sx, sy > 1 → aproxima (crop)
    print(f"Aplicando escala: sx={sx}, sy={sy}")
    print(f"Imagem shape: {img.shape}")
    h, w, _ = img.shape

    cx = (w) / 2
    cy = (h) / 2

    # Amplia a imagem em relação ao centro, então a escala é aplicada em relação ao centro
    m = inv_translation_matrix(-cx, -cy) @ inv_scale_matrix(sx, sy) @ inv_translation_matrix(cx, cy)

    clamped = False
    for i in range(h):
        for j in range(w):
            p = np.array([j, i, 1])
            p_new = m @ p

            x_new = int(p_new[0])
            y_new = int(p_new[1])
            # Avisa se o pixel de origem está fora dos limites da imagem original, mas aplica clamping para evitar pixels vazios

            if not (0 <= x_new < w and 0 <= y_new < h):
                clamped = True
            x_src = np.clip(x_new, 0, w - 1)
            y_src = np.clip(y_new, 0, h - 1)
            new_img[i, j] = img[y_src, x_src]

    return new_img, clamped






# --- Função principal ---

def transform_image(img, transform_type, params):
    # Ponto de entrada chamado por app.py para cada etapa do pipeline.
    # Recebe a imagem como array NumPy, o tipo de transformação e seus parâmetros.
    # Retorna (imagem_transformada, lista_de_avisos).
    new_img = np.zeros_like(img)
    warnings = []
    print(f"Transformação solicitada: {transform_type} com parâmetros {params}")

    if transform_type == 'translation':
        dx = params['dx']
        dy = params['dy']
        result, clamped = apply_translation(img, new_img, dx, dy)
        if clamped:
            warnings.append(
                f"Translação (dx={dx}, dy={dy}): pixels que mapeariam fora da imagem "
                f"foram substituídos pelo pixel de borda mais próximo (clamping)."
            )
        return result, warnings

    if transform_type == 'rotation':
        angle = params['angle']
        theta = np.pi * angle / 180
        result, clamped = apply_rotation(img, new_img, theta)
        if clamped:
            warnings.append(
                f"Rotação ({angle}°): pixels dos cantos que mapeariam fora da imagem "
                f"foram substituídos pelo pixel de borda mais próximo (clamping)."
            )
        return result, warnings

    if transform_type == 'scale':
        sx = params['sx']
        sy = params['sy']
        result, clamped = apply_scale(img, new_img, sx, sy)
        if clamped:
            warnings.append(
                f"Escala (sx={sx}, sy={sy}): pixels que mapeariam fora da imagem "
                f"foram substituídos pelo pixel de borda mais próximo (clamping)."
            )
        return result, warnings

    if transform_type == 'inverse':
        return f_inv(img), warnings

    if transform_type == 'log':
        return f_log(img), warnings

    if transform_type == 'gamma':
        return f_gamma(img, params['gamma']), warnings

    if transform_type == 'contrast':
        a = params['a']
        b = params['b']
        c = params['c']
        d = params['d']
        return f_mod(img, a=a, b=b, c=c, d=d), warnings

    if transform_type == 'creative':
        L = params.get('L', 128)
        return f_threshold(img, L=L), warnings

    return new_img, warnings
    
