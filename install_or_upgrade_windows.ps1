$root = "C:\ENDO-SYM\project"
$final = "C:\ENDO-SYM\project\spriteforge project"

New-Item -ItemType Directory -Path $root -Force | Out-Null

if (Test-Path $final) {
    Write-Host "Encontrado projeto antigo em: $final"
    Write-Host "Criando backup..."
    $backup = "C:\ENDO-SYM\project\spriteforge project backup " + (Get-Date -Format "yyyyMMdd_HHmmss")
    Copy-Item -LiteralPath $final -Destination $backup -Recurse -Force
    Write-Host "Backup criado em: $backup"
}

Write-Host "Copie os arquivos da pasta SpriteForge_v02 para:"
Write-Host $final
Write-Host "Depois rode:"
Write-Host "cd `"$final`""
Write-Host "python -m pip install -r requirements.txt"
Write-Host "python examples\run_all.py"
