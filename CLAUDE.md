# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the project

```bash
pip install -r requirements.txt
python app.py
```

Server runs at **http://localhost:5001**. The Flask app serves the frontend statically from the `front/` directory, so no separate frontend server is needed.

## Architecture

**Backend** (`app.py`): Single Flask route `/process` (POST) that receives a base64-encoded image and a `pipeline` array of transforms, applies them in order via `photoshop.transform_image()`, and returns the result as base64 JPEG.

**Image processing** (`photoshop.py`): All transformations live here. The entry point is:
```python
transform_image(img: np.ndarray, transform_type: str, params: dict) -> np.ndarray
```
Supported `transform_type` values and their params:

| `transform_type` | Params | Formula / method |
|---|---|---|
| `translation` | `dx`, `dy` (px) | Inverse mapping: each output pixel samples from `img[y-dy, x-dx]`. Pixels that map outside the image are black. |
| `rotation` | `angle` (degrees) | Converted to radians; inverse rotation matrix applied around image center. Pixels outside bounds are black. |
| `scale` | `sx`, `sy` (float, e.g. 1.0) | Inverse scale matrix applied around image center. Values <1 zoom out (black borders); >1 zoom in (crops). |
| `inverse` | — | `f(x) = 255 - x` per channel. |
| `gamma` | `gamma` (float) | `f(x) = x^(1/γ) * 255 / 255^(1/γ)`. γ<1 brightens, γ>1 darkens. |
| `contrast` | `a`, `b`, `c`, `d` (0–255) | Piecewise linear: `[0,a]→[0,c]`, `[a,b]→[c,d]`, `[b,255]→[d,255]`. Saves a debug curve to `debug_curves/`. |
| `creative` | `media` (μ, 0–255), `sigma` (σ, 1–100) | Sigmoidal: `f(x) = 1/(1+e^(-(x-μ)/σ)) * 255`. Saves a debug curve to `debug_curves/`. |

Geometric transforms use per-pixel inverse mapping with homogeneous 3×3 matrices (`inv_translation_matrix`, `inv_rot_matrix`, `inv_scale_matrix`). Intensity transforms vectorise directly over the numpy array.

**Frontend** (`front/`): Single-page app. `script.js` holds all logic — the `configs` object maps each transform type to its UI render/bind/params functions. The pipeline is a JS array of `{type, params, color}` objects sent as JSON to the backend.

## Key constraints

- **All image transformations must be implemented in `photoshop.py` only.** Do not add image processing logic to `app.py` or the frontend.
- The backend uses `imageio.v3` for image I/O (not Pillow, despite Pillow being in `requirements.txt`).
- Input images arrive as JPEG (no alpha channel). The backend strips alpha if present before saving with imageio.
- Debug curve plots are saved to `debug_curves/` and a `debug_output.jpg` is written on every request — both are development artifacts.

## Adding a new transform

1. Implement the function in `photoshop.py`
2. Add a branch in `transform_image()` for the new `transform_type` string
3. Add a button in `front/index.html` with `data-type="<type>"`
4. Add the corresponding entry to the `configs` object in `front/script.js` (with `render`, `bind`, `params`, `label`, `color`)
