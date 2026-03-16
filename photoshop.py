import imageio.v3 as iio
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from pathlib import Path


def inv_translation_matrix(ti, tj):
    return np.array([[1, 0, -ti],
            [0, 1, -tj],
            [0, 0, 1]])

def inv_rot_matrix(theta):
    return np.array([[np.cos(theta), np.sin(theta), 0],
            [-np.sin(theta), np.cos(theta), 0],
            [0, 0, 1]])

def inv_scale_matrix(si, sj):
    return np.array([[1.0 / si, 0, 0],
            [0, 1.0 / sj, 0],
            [0, 0, 1]] )

def f_inv(light):
    return 255-light    

def f_log(light):
    img = np.log(light.astype(float)+1)
    img = img * 255/np.log(255+1)
    return img.astype(np.uint8)

def f_gamma(light, gamma=2.2):
    img = light.astype(float)**(1/gamma)
    img = img * 255/(255**(1/gamma))
    return img.astype(np.uint8)



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
    

def save_f_mod_sigmoid_curve(mu=128, sigma=30):
    # Create an array for input values (0 to 255)
    x = np.arange(256, dtype=float)
    
    # Apply the sigmoidal transformation
    y = 1 / (1 + np.exp(-(x - mu) / sigma))
    y = np.clip(y * 255, 0, 255)  # Scale back to 0-255 range

    # Define output directory and file path
    output_dir = Path(__file__).resolve().parent / "debug_curves"
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    output_file = output_dir / f"f_mod_sigmoid_mu{mu}_sigma{sigma}_{timestamp}.png"

    # Plot the transformation curve
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(x, y, color='tab:blue', linewidth=2, label='Sigmoidal Transformation')
    ax.set_title(f"Sigmoidal Transformation: mu={mu}, sigma={sigma}")
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
    print(f"Curva sigmoidal salva em: {output_file}")


def f_mod_sigmoid(img, mu=128, sigma=30):
    try:
        img_float = img.astype(float)
        img_float = 1 / (1 + np.exp(-(img_float - mu) / sigma))
        img_float = np.clip(img_float * 255, 0, 255)
        save_f_mod_sigmoid_curve(mu, sigma)
        return img_float.astype(np.uint8)
    except Exception as error:
        print(f"Error during sigmoidal transformation: {error}")
        return img


def apply_translation(img, new_img, dx, dy):
    print(f"Aplicando translação: dx={dx}, dy={dy}")
    print(f"Imagem shape: {img.shape}")
    h, w, _ = img.shape
    m = inv_translation_matrix(dx, dy)
    for i in range(h):
        for j in range(w):
            p = np.array([j, i, 1])
            p_new = m @ p

            x_new = int(p_new[0])
            y_new = int(p_new[1])

            if 0 <= x_new < w and 0 <= y_new < h:
                new_img[i, j] = img[y_new, x_new]
    return new_img

def apply_rotation(img, new_img, theta):
    print(f"Aplicando rotação: theta={theta} radianos")
    print(f"Imagem shape: {img.shape}")
    h, w, _ = img.shape

    cx = (w) / 2
    cy = (h) / 2
    m = inv_translation_matrix(-cx, -cy) @ inv_rot_matrix(theta) @ inv_translation_matrix(cx, cy)
    
    for i in range(h):
        for j in range(w):
            p = np.array([j, i, 1])
            p_new = m @ p

            x_new = int(p_new[0])
            y_new = int(p_new[1])

            if 0 <= x_new < w and 0 <= y_new < h:
                new_img[i, j] = img[y_new, x_new]
    return new_img

def apply_scale(img, new_img, sx, sy):
    print(f"Aplicando escala: sx={sx}, sy={sy}")
    print(f"Imagem shape: {img.shape}")
    h, w, _ = img.shape

    cx = (w) / 2
    cy = (h) / 2

    # Amplia a imagem em relação ao centro, então a escala é aplicada em relação ao centro
    m = inv_translation_matrix(-cx, -cy) @ inv_scale_matrix(sx, sy) @ inv_translation_matrix(cx, cy)
    
    for i in range(h):
        for j in range(w):
            p = np.array([j, i, 1])
            p_new = m @ p

            x_new = int(p_new[0])
            y_new = int(p_new[1])

            if 0 <= x_new < w and 0 <= y_new < h:
                new_img[i, j] = img[y_new, x_new]

    return new_img

def transform_image(img, transform_type, params):
    new_img = np.zeros_like(img)
    print(f"Transformação solicitada: {transform_type} com parâmetros {params}")    
    if transform_type == 'translation':
        dx = params['dx']
        dy = params['dy']
        return apply_translation(img, new_img, dx, dy)
    
    if transform_type == 'rotation':
        # Transforma theta em radianos
        angle = params['angle']
        theta = np.pi * angle / 180
        return apply_rotation(img, new_img, theta)
    
    if transform_type == 'scale':

        sx = params['sx']
        sy = params['sy']
        return apply_scale(img, new_img, sx, sy)
    
    if transform_type == 'inverse':
        return f_inv(img)

    if transform_type == 'gamma':
        return f_gamma(img, params['gamma'])    

    if transform_type == 'contrast':
        a = params['a']
        b = params['b']
        c = params['c']
        d = params['d']

        return f_mod(img, a=a, b=b, c=c, d=d)

    if transform_type == 'creative':
        media = params.get('media', 128)
        sigma = params.get('sigma', 30)
        return f_mod_sigmoid(img, mu=media, sigma=sigma)
    

    return new_img
    
