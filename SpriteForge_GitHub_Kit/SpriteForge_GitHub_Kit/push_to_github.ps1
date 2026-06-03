# Rode este script dentro da pasta do projeto SpriteForge.
# Caminho esperado:
# C:\END0-SYM\project\spriteforge project

Set-Location -LiteralPath "C:\END0-SYM\project\spriteforge project"

Write-Host "Inicializando Git..."
git init

Write-Host "Adicionando arquivos..."
git add .

Write-Host "Criando commit..."
git commit -m "Initial SpriteForge prototype"

Write-Host "Renomeando branch para main..."
git branch -M main

Write-Host "Adicione o remote depois de criar o repo no GitHub:"
Write-Host "git remote add origin https://github.com/macksonvictor/spriteforge.git"
Write-Host "git push -u origin main"
