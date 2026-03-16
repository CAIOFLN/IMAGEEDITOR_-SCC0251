# IMAGE EDITOR - SCC0251
**Processamento de Imagens**

## 🚀 Como executar

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Iniciar o servidor Flask
```bash
python app.py
```

### 3. Acessar a aplicação
Abra o navegador em: **http://localhost:5000**

## 📝 Transformações disponíveis

### Geométricas
- **Translação**: Desloca a imagem com wrap circular
- **Rotação**: Rotaciona ao redor do centro
- **Escala**: Redimensiona a imagem

### Intensidade
- **Inversa**: f(x) = 255 - x
- **Log**: f(x) = c · log(1 + x)
- **Gama**: f(x) = c · x^γ
- **Contraste**: Mapeia [a, b] → [0, 255]
- **Solarize**: Efeito fotográfico artístico

## 🎨 Como usar
1. Clique em "IMAGE INPUT" para carregar uma imagem
2. Selecione uma transformação e ajuste os parâmetros
3. Clique em "+ ADICIONAR À PIPELINE" 
4. Repita para adicionar mais transformações
5. Clique em "▶ PROCESSAR" para aplicar
6. Baixe o resultado com "BAIXAR RESULTADO"
