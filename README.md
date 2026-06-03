# SpriteForge v0.7 Asset Families + Real Variations + Packs

SpriteForge e um gerador gratuito de assets em pixel art para jogos 2D.

Ele recebe prompts como:

```bash
python main.py "sapo ninja com espada de fogo, 6 frames, 32x32"
```

E exporta frames PNG, spritesheet PNG, GIF preview e metadata JSON na pasta:

```text
outputs
```

## Novidade da v0.7

A v0.7 usa um planejamento interno mais rico para gerar assets por familias:

- criaturas
- itens
- efeitos
- cenarios

Mesmo quando nao existe um gerador especifico, o SpriteForge escolhe uma familia, um template base, acessorios e elementos para criar uma aproximacao visual consistente.

Agora tambem existem variacoes reais com `seed` e `variant_id`. Um prompt como:

```bash
python main.py "sapo ninja com espada de fogo, 6 frames, 32x32, variacao 2"
```

gera um asset com sufixo de variacao, por exemplo:

```text
sapo_idle_32x32_6frames_v002
```

## Packs

A v0.7 tambem cria packs simples de personagem/criatura:

```bash
python main.py "pack sapo ninja com espada de fogo, 32x32"
```

O pack gera animacoes em:

```text
outputs/packs/sapo_ninja_fire_sword/idle
outputs/packs/sapo_ninja_fire_sword/walk
outputs/packs/sapo_ninja_fire_sword/jump
outputs/packs/sapo_ninja_fire_sword/attack
```

## Abrir o Studio

O Studio e uma interface local simples com Tkinter.

Para abrir:

```bash
python studio.py
```

No Windows, tambem da para clicar em:

```text
run_studio.bat
```

## Como usar o Studio

1. Escreva um prompt ou clique em um exemplo pronto.
2. Clique em **Gerar Asset**.
3. Veja o nome do asset, generator, fallback, output, metadata e caminho do GIF.
4. Use **Abrir GIF** para ver a preview gerada.
5. Use **Abrir ultimo asset** para abrir a pasta do asset gerado.
6. Use **Abrir pasta de outputs** para abrir a pasta geral `outputs`.

O Studio tambem mostra um historico simples da sessao. Ao clicar em um item do historico, o prompt usado volta para a caixa de texto e os botoes passam a abrir aquele asset.

Prompts sem gerador especifico usam fallback generico, como `generic.creature`, `generic.effect`, `generic.item` ou `generic.background`.

Use **Gerar variação** para criar uma variante visual sem sobrescrever o asset anterior. Use **Gerar pack** para criar um pack simples com idle, walk, jump e attack.

## Rodar pelo terminal

```bash
python main.py "sapo ninja com espada de fogo, 6 frames, 32x32"
```

Outros exemplos:

```bash
python main.py "capivara de armadura andando, 8 frames, 32x32"
python main.py "monstro de pedra com olhos vermelhos, 6 frames, 32x32"
python main.py "portal dimensional roxo girando, 8 frames, 64x64"
python main.py "floresta escura para jogo plataforma, 1 frame, 96x48"
```

## Geradores especificos mantidos

```bash
python main.py "robo correndo, 8 frames, 32x32, azul neon"
python main.py "slime verde pulando, 6 frames, 32x32"
python main.py "espada magica brilhando, 4 frames, 32x32, azul"
python main.py "estrela piscando, 5 frames, 16x16"
python main.py "explosao de fogo, 8 frames, 48x48"
```

## Testes manuais

```bash
python examples\run_all.py
python examples\test_quality_v04.py
python examples\test_universal_v06.py
python examples\test_v07_assets_and_packs.py
```

## Logs

Pedidos realmente desconhecidos sao registrados em:

```text
spriteforge/logs/unknown_requests.jsonl
```
