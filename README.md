# IMAGE EDITOR - SCC0251
**Processamento de Imagens — Caio Florentin de Oliveira (NUSP: 14562921)**

## Como executar

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Iniciar o servidor Flask
```bash
python app.py
```

### 3. Acessar a aplicação
Abra o navegador em: **http://localhost:5001**

## Transformações disponíveis

### Geométricas
Todas usam **mapeamento inverso** com matrizes homogêneas 3×3. Pixels que mapeiam fora dos limites recebem o valor do pixel de borda mais próximo (*border clamping*).

- **Translação** (`dx`, `dy`): desloca a imagem horizontalmente e verticalmente
- **Rotação** (`angle`): rotaciona em torno do centro da imagem
- **Escala** (`sx`, `sy`): redimensiona em relação ao centro da imagem

### Intensidade
Aplicadas canal a canal (RGB independentes), exceto o Limiar.

- **Inversa**: `f(x) = 255 - x`
- **Log**: `f(x) = log(x+1) / log(256) * 255`
- **Gama** (`gamma`): `f(x) = x^(1/γ) * 255 / 255^(1/γ)`
- **Contraste** (`a`, `b`, `c`, `d`): transformação linear por partes com pontos de controle `[0,a]→[0,c]`, `[a,b]→[c,d]`, `[b,255]→[d,255]`
- **Limiar** (`L`): mantém pixels cuja luminância supera `L`, zera os demais

## Como usar
1. Clique em "IMAGE INPUT" para carregar uma imagem JPEG
2. Selecione uma transformação e ajuste os parâmetros
3. Clique em "+ ADICIONAR À PIPELINE"
4. Repita para adicionar mais transformações
5. Clique em "PROCESSAR" para aplicar
6. Baixe o resultado com "BAIXAR RESULTADO"
