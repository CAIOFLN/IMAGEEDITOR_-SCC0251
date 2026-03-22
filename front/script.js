// Nome: [Caio FLorentin de Oliveira] | NUSP: [14562921]
// SCC0251 - Processamento de Imagens

// Variáveis globais
let originalImageData = null;
let pipeline = [];
let selectedType = null;

// Elementos do DOM (Document Object Model)
const imageUpload = document.getElementById('imageUpload');

// Canvas = elemento HTML5 para desenhar/manipular imagens pixel por pixel
const canvasEntrada = document.getElementById('canvasEntrada');
const canvasSaida = document.getElementById('canvasSaida');

// Contexto 2D = interface para desenhar no canvas
const ctxEntrada = canvasEntrada.getContext('2d', { willReadFrequently: true });
const ctxSaida = canvasSaida.getContext('2d');

const containerEntrada = document.getElementById('containerEntrada');
const containerSaida = document.getElementById('containerSaida');
const placeholderEntrada = document.getElementById('placeholderEntrada');
const placeholderSaida = document.getElementById('placeholderSaida');
const tituloControle = document.getElementById('tituloControle');
const conteudoControle = document.getElementById('conteudoControle');
const botaoAdicionarPipeline = document.getElementById('botaoAdicionarPipeline');
const botaoProcessar = document.getElementById('botaoProcessar');
const botaoLimparPipeline = document.getElementById('botaoLimparPipeline');
const listaPipeline = document.getElementById('listaPipeline');
const botaoBaixar = document.getElementById('botaoBaixar');

// Carregamento de imagem
containerEntrada.addEventListener('click', () => imageUpload.click());

imageUpload.addEventListener('change', (evento) => {
  const arquivo = evento.target.files[0];
  if (!arquivo) return;

  const imagem = new Image();
  imagem.onload = () => {
    // Ajusta o tamanho dos canvas para o tamanho da imagem
    canvasEntrada.width = imagem.naturalWidth;
    canvasEntrada.height = imagem.naturalHeight;
    canvasSaida.width = imagem.naturalWidth;
    canvasSaida.height = imagem.naturalHeight;

    // Desenha a imagem no canvas de entrada
    ctxEntrada.drawImage(imagem, 0, 0);
    // getImageData = pega os dados dos pixels (RGBA) da imagem
    originalImageData = ctxEntrada.getImageData(0, 0, canvasEntrada.width, canvasEntrada.height);

    // Mostra o canvas de entrada
    canvasEntrada.style.display = 'block';
    placeholderEntrada.style.display = 'none';
    botaoProcessar.disabled = false;

    // Reseta o canvas de saída
    ctxSaida.clearRect(0, 0, canvasSaida.width, canvasSaida.height);
    canvasSaida.style.display = 'none';
    placeholderSaida.style.display = '';
    botaoBaixar.disabled = true;

    URL.revokeObjectURL(imagem.src);
  };
  imagem.src = URL.createObjectURL(arquivo);
  imageUpload.value = '';
});

// Seleção de transformação
document.querySelectorAll('.transform-btn').forEach(botao => {
  botao.addEventListener('click', () => {
    // Remove a classe active de todos os botões
    document.querySelectorAll('.transform-btn').forEach(b => b.classList.remove('active'));
    // Adiciona active no botão clicado
    botao.classList.add('active');
    selectedType = botao.dataset.type;
    renderControlPanel(selectedType);
    botaoAdicionarPipeline.disabled = false;
  });
});

// Configurações de cada transformação
const configs = {
  translation: {
    title: 'TRANSLAÇÃO',
    render: () => {
      const maxX = canvasEntrada.width || 500;
      const maxY = canvasEntrada.height || 500;
      return `
      <div class="transform-desc">Desloca todos os pixels por (dx, dy). Pixels fora dos limites ficam pretos.</div>
      <div class="control-field">
        <label>DESLOCAMENTO X <span class="val" id="dxVal">0 px</span></label>
        <input type="range" class="slider" id="dx" min="${-maxX}" max="${maxX}" value="0">
      </div>
      <div class="control-field">
        <label>DESLOCAMENTO Y <span class="val" id="dyVal">0 px</span></label>
        <input type="range" class="slider" id="dy" min="${-maxY}" max="${maxY}" value="0">
      </div>`;
    },
    bind: () => {
      const dx = document.getElementById('dx');
      const dy = document.getElementById('dy');
      dx.addEventListener('input', () => { document.getElementById('dxVal').textContent = dx.value + ' px'; });
      dy.addEventListener('input', () => { document.getElementById('dyVal').textContent = dy.value + ' px'; });
    },
    params: () => ({ dx: +document.getElementById('dx').value, dy: +document.getElementById('dy').value }),
    label:  (p) => `dx=${p.dx} dy=${p.dy}`,
    color:  '#f97316',
  },
  rotation: {
    title: 'ROTAÇÃO',
    render: () => `
      <div class="transform-desc">Rotaciona a imagem ao redor do centro. Pixels fora dos limites são descartados.</div>
      <div class="control-field">
        <label>ÂNGULO <span class="val" id="angleVal">0°</span></label>
        <input type="range" class="slider" id="angle" min="-180" max="180" value="0">
      </div>`,
    bind: () => {
      const a = document.getElementById('angle');
      a.addEventListener('input', () => { document.getElementById('angleVal').textContent = a.value + '°'; });
    },
    params: () => ({ angle: +document.getElementById('angle').value }),
    label:  (p) => `${p.angle}°`,
    color:  '#14b8a6',
  },
  scale: {
    title: 'ESCALA',
    render: () => `
      <div class="transform-desc">Aumenta ou reduz a imagem ao redor do centro. Pixels fora dos limites são descartados.</div>
      <div class="control-field">
        <label>FATOR X <span class="val" id="scaleXVal">1.0×</span></label>
        <input type="range" class="slider" id="scaleX" min="2" max="80" value="10">
      </div>
      <div class="control-field">
        <label>FATOR Y <span class="val" id="scaleYVal">1.0×</span></label>
        <input type="range" class="slider" id="scaleY" min="2" max="80" value="10">
      </div>`,
    bind: () => {
      const sx = document.getElementById('scaleX');
      const sy = document.getElementById('scaleY');
      sx.addEventListener('input', () => { document.getElementById('scaleXVal').textContent = (sx.value / 10).toFixed(1) + '×'; });
      sy.addEventListener('input', () => { document.getElementById('scaleYVal').textContent = (sy.value / 10).toFixed(1) + '×'; });
    },
    params: () => ({ sx: document.getElementById('scaleX').value / 10, sy: document.getElementById('scaleY').value / 10 }),
    label:  (p) => `sx=${(+p.sx).toFixed(1)}× sy=${(+p.sy).toFixed(1)}×`,
    color:  '#a855f7',
  },
  inverse: {
    title: 'INVERSA',
    render: () => `<div class="transform-desc">f(x) = 255 − x<br><br>Inverte todos os valores de intensidade de cada canal RGB.</div>`,
    bind: () => {},
    params: () => ({}),
    label:  () => '',
    color:  '#ef4444',
  },
  log: {
    title: 'TRANSFORMAÇÃO LOG',
    render: () => `<div class="transform-desc">f(x) = c · log(1 + x) &nbsp;| &nbsp;c = 255 / log(256)<br><br>Expande tons escuros e comprime tons claros.</div>`,
    bind: () => {},
    params: () => ({}),
    label:  () => '',
    color:  '#eab308',
  },
  gamma: {
    title: 'CORREÇÃO GAMA',
    render: () => `
      <div class="transform-desc">f(x) = c · x^γ &nbsp;(c = 255 / 255^γ)<br>γ &lt; 1 → clareia &nbsp;|&nbsp; γ &gt; 1 → escurece</div>
      <div class="control-field">
        <label>γ (GAMMA) <span class="val" id="gammaVal">1.0</span></label>
        <input type="range" class="slider" id="gamma" min="1" max="50" value="10">
      </div>`,
    bind: () => {
      const g = document.getElementById('gamma');
      g.addEventListener('input', () => { document.getElementById('gammaVal').textContent = (g.value / 10).toFixed(1); });
    },
    params: () => ({ gamma: document.getElementById('gamma').value / 10 }),
    label:  (p) => `γ=${(+p.gamma).toFixed(1)}`,
    color:  '#22c55e',
  },
  contrast: {
    title: 'MODULAÇÃO DE CONTRASTE',
    render: () => `
      <div class="transform-desc">Mapeia o intervalo de entrada [a, b] para [c, d]. Valores fora do intervalo são recortados.</div>
      <div class="inline-inputs">
        <div class="control-field">
          <label>a — MIN IN</label>
          <input type="number" class="number-input" id="contrastA" value="30"  min="0" max="254">
        </div>
        <div class="control-field">
          <label>b — MAX IN</label>
          <input type="number" class="number-input" id="contrastB" value="200" min="1" max="255">
        </div>
        <div class="control-field">
          <label>c — MIN OUT</label>
          <input type="number" class="number-input" id="contrastC" value="0"   min="0" max="255">
        </div>
        <div class="control-field">
          <label>d — MAX OUT</label>
          <input type="number" class="number-input" id="contrastD" value="255" min="0" max="255">
        </div>
      </div>`,
    bind: () => {},
    params: () => ({
      a: Math.min(+document.getElementById('contrastA').value, +document.getElementById('contrastB').value - 1),
      b: +document.getElementById('contrastB').value,
      c: +document.getElementById('contrastC').value,
      d: +document.getElementById('contrastD').value,
    }),
    label:  (p) => `[${p.a},${p.b}]→[${p.c},${p.d}]`,
    color:  '#3b82f6',
  },
  creative: {
    title: 'TRANSFORMAÇÃO CRIATIVA',
    render: () => `
      <div class="transform-desc">out_pixel = 1 / (1 + e<sup>-(x - μ)/σ</sup>)<br><br>μ controla o centro da curva e σ controla a inclinação.</div>
      <div class="inline-inputs">
        <div class="control-field">
          <label>μ — MÉDIA <span class="val" id="sigmoidMediaVal">128</span></label>
          <input type="range" class="slider" id="sigmoidMedia" min="0" max="255" value="128">
        </div>
        <div class="control-field">
          <label>σ — SIGMA <span class="val" id="sigmoidSigmaVal">30</span></label>
          <input type="range" class="slider" id="sigmoidSigma" min="1" max="100" value="30">
        </div>
      </div>`,
    bind: () => {
      const media = document.getElementById('sigmoidMedia');
      const sigma = document.getElementById('sigmoidSigma');
      media.addEventListener('input', () => { document.getElementById('sigmoidMediaVal').textContent = media.value; });
      sigma.addEventListener('input', () => { document.getElementById('sigmoidSigmaVal').textContent = sigma.value; });
    },
    params: () => ({ media: +document.getElementById('sigmoidMedia').value, sigma: +document.getElementById('sigmoidSigma').value }),
    label:  (p) => `μ=${p.media} σ=${p.sigma}`,
    color:  '#ec4899',
  },
};

function renderControlPanel(tipo) {
  const config = configs[tipo];
  tituloControle.textContent = config.title;
  conteudoControle.innerHTML = config.render();
  config.bind();
}

// Adicionar transformação à pipeline
botaoAdicionarPipeline.addEventListener('click', () => {
  if (!selectedType) return;
  const config = configs[selectedType];
  pipeline.push({ type: selectedType, params: config.params(), color: config.color });
  renderPipeline();
});

// Nomes das transformações para exibição
const typeNames = {
  translation: 'Translação', rotation: 'Rotação',  scale:    'Escala',
  inverse:     'Inversa',    log:      'Log',        gamma:    'Gama',
  contrast:    'Contraste',  creative: 'Criativa',
};

// Renderiza a lista de transformações na pipeline
function renderPipeline() {
  if (pipeline.length === 0) {
    listaPipeline.innerHTML = '<div class="pipeline-empty">Nenhuma transformação adicionada</div>';
    return;
  }
  listaPipeline.innerHTML = pipeline.map((item, indice) => {
    const rotulo = configs[item.type].label(item.params);
    return `
      <div class="pipeline-item">
        <div class="pipeline-item-left">
          <span class="pipeline-dot" style="background:${item.color}"></span>
          <span class="pipeline-num">${indice + 1}.</span>
          <span class="pipeline-name">${typeNames[item.type]}</span>
          ${rotulo ? `<span class="pipeline-params">${rotulo}</span>` : ''}
        </div>
        <button class="pipeline-remove" onclick="removeItem(${indice})" title="Remover">✕</button>
      </div>`;
  }).join('');
}

// Remove um item da pipeline
function removeItem(indice) {
  pipeline.splice(indice, 1);
  renderPipeline();
}

// Limpa toda a pipeline
botaoLimparPipeline.addEventListener('click', () => {
  pipeline = [];
  renderPipeline();
});

// Processar imagem
botaoProcessar.addEventListener('click', async () => {
  if (!originalImageData || pipeline.length === 0) {
    if (pipeline.length === 0) {
      alert('Adicione pelo menos uma transformação à pipeline!');
    }
    return;
  }

  // Esconde aviso de clamping anterior
  document.getElementById('avisoClamp').style.display = 'none';

  // Mostra overlay de processamento
  const overlay = document.createElement('div');
  overlay.className = 'processing-overlay';
  overlay.textContent = 'PROCESSANDO...';
  containerSaida.appendChild(overlay);
  botaoProcessar.disabled = true;

  try {
    // Converte o canvas original para base64
    const imageDataURL = canvasEntrada.toDataURL('image/jpeg', 1);

    // Envia para o backend Flask (URL relativa)
    const response = await fetch('/process', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        image: imageDataURL,
        pipeline: pipeline
      })
    });

    const result = await response.json();

    if (result.success) {
      // Exibe aviso de clamping se houver
      const avisoClamp = document.getElementById('avisoClamp');
      if (result.warnings && result.warnings.length > 0) {
        document.getElementById('avisoClampTexto').innerHTML =
          '<strong>Aviso — clamping aplicado:</strong><br>' +
          result.warnings.map(w => '• ' + w).join('<br>');
        avisoClamp.style.display = 'flex';
      } else {
        avisoClamp.style.display = 'none';
      }

      // Carrega a imagem processada retornada pelo backend
      const imagemProcessada = new Image();
      imagemProcessada.onload = () => {
        canvasSaida.width = imagemProcessada.width;
        canvasSaida.height = imagemProcessada.height;
        ctxSaida.drawImage(imagemProcessada, 0, 0);

        canvasSaida.style.display = 'block';
        placeholderSaida.style.display = 'none';
        botaoBaixar.disabled = false;
      };
      imagemProcessada.src = result.image;
    } else {
      alert('Erro ao processar imagem: ' + result.error);
    }
  } catch (error) {
    console.error('Erro:', error);
    alert('Erro ao processar imagem. Verifique o console para mais detalhes.');
  } finally {
    overlay.remove();
    botaoProcessar.disabled = false;
  }
});

// Download da imagem processada
botaoBaixar.addEventListener('click', () => {
  const link = document.createElement('a');
  link.download = 'output.jpg';
  link.href = canvasSaida.toDataURL('image/jpeg', 0.95);
  link.click();
});
