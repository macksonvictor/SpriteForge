# SpriteForge

SpriteForge é um gerador gratuito de assets em pixel art para jogos 2D.

A visão do projeto é permitir que uma pessoa escreva uma ideia, como:

```text
sapo ninja com espada de fogo, 6 frames, 32x32
portal dimensional roxo girando, 8 frames, 64x64
floresta escura para jogo plataforma, 1 frame, 96x48
```

e receba assets exportáveis para jogos:

- frames PNG
- spritesheet PNG
- GIF de preview
- metadata JSON

## Estado atual

O projeto já possui:

- motor base `SpriteForge().generate(prompt)`
- interface local `studio.py`
- exportação para `outputs/`
- geradores específicos e genéricos
- início de variações, packs e histórico

Ainda não está pronto como produto final. É um protótipo em evolução.

## Como rodar

```powershell
cd "C:\END0-SYM\project\spriteforge project"
python studio.py
```

Ou pelo terminal:

```powershell
python main.py "sapo ninja pulando com espada de fogo, 6 frames, 32x32"
```

## Direção futura

A prioridade técnica é criar o **Prompt to PixelScript Engine**, para que o SpriteForge consiga gerar uma variedade muito maior de assets sem depender de um gerador manual para cada coisa.

Veja o arquivo `ROADMAP.md`.
