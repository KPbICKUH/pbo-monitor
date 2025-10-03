# animation_install.ps1
$frames = @(
    "Установка Python.   ",
    "Установка Python..  ",
    "Установка Python... "
)

# Показываем анимацию 5 секунд
$endTime = (Get-Date).AddSeconds(5)
while ((Get-Date) -lt $endTime) {
    foreach ($f in $frames) {
        Write-Host "`r$f" -NoNewline
        Start-Sleep -Milliseconds 300
    }
}
Write-Host "" # новая строка