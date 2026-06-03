# SpriteForge Roadmap

## Objetivo geral

Transformar o SpriteForge em um gerador gratuito de assets pixel art para jogos 2D, com suporte a personagens, itens, efeitos, cenários, animações e packs exportáveis.

## v0.9 — Prompt to PixelScript Engine

Criar a base universal de desenho procedural.

Tarefas:

- criar `spriteforge/pixelscript/`
- criar `parser.py`, `renderer.py`, `builder.py`
- criar `spriteforge/universal_planner.py`
- transformar prompt em plano visual
- transformar plano visual em PixelScript
- renderizar PixelScript para frames
- integrar no `core.py`

## v1.0 — Studio organizado

Melhorar a interface local.

Tarefas:

- limpar layout do Studio
- melhorar preview
- mostrar engine usada: specific/generic/pixelscript
- mostrar metadata resumida
- permitir ver PixelScript gerado

## v1.1 — Quality Engine

Melhorar qualidade visual.

Tarefas:

- criar biblioteca de partes pixel art
- criar score simples de qualidade
- melhorar silhueta, pose, contorno e animação
- salvar `quality_score` e `quality_notes` no metadata

## v1.2 — Variações reais

Tarefas:

- implementar `seed`
- implementar `variant_id`
- gerar variações visuais reais
- evitar sobrescrita de assets

## v1.3 — Packs de personagem

Tarefas:

- gerar idle, walk, jump e attack para o mesmo personagem
- manter identidade visual entre animações
- exportar pasta de pack

## v1.4 — Exportação para jogos

Tarefas:

- export para Godot
- export para Unity
- spritesheet + metadata organizada
- pacotes prontos para prototipagem
