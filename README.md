# Air Mouse

Controle seu computador com gestos de mão capturados pela webcam — sem tocar no teclado ou mouse.

## Gestos

| Gesto | Ação |
|-------|------|
| ☝️✌️ Dois dedos para cima, movendo | Scroll (sobe/desce conforme direção) |
| 🤏 Pinça (polegar + indicador se tocam) | Minimizar janela ativa |
| ✊ Punho fechado | Fechar janela ativa |

> **Atenção:** o gesto de fechar janela tem debounce de 2 segundos para evitar acidentes.

## Requisitos

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (gerenciador de pacotes)
- Linux: `xdotool` instalado

```bash
# Linux
sudo apt install xdotool
```

## Instalação

```bash
git clone <repo>
cd air-mouse

uv venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

uv pip install -r requirements.txt
```

## Uso

```bash
# Modo silencioso (background, sem janela)
python main.py

# Modo showcase (janela com overlay dos landmarks)
python main.py --showcase

# Opções
python main.py --cam 1          # usar câmera de índice 1
python main.py --sensitivity 50 # scroll mais rápido (default: 30)
```

Pressione `q` ou `ESC` para sair do modo showcase.  
Pressione `Ctrl+C` para sair do modo silencioso.

## Como funciona

O projeto usa [MediaPipe Hands](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker) para detectar 21 pontos da mão em tempo real via webcam. A partir desses pontos, são identificados três gestos:

- **Scroll**: indicador e médio levantados se movem — o delta vertical é convertido em scroll da página.
- **Pinça**: distância entre polegar e indicador abaixo de um limiar → `xdotool key super+Down`.
- **Punho**: todas as pontas dos dedos abaixo das juntas → `xdotool key alt+F4`.

No modo showcase, os landmarks são desenhados sobre o feed da webcam com cores que indicam o gesto ativo.
