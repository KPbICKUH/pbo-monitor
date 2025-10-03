# animation_install.ps1
$frames = @(
    "��������� Python.   ",
    "��������� Python..  ",
    "��������� Python... "
)

# ���������� �������� 5 ������
$endTime = (Get-Date).AddSeconds(5)
while ((Get-Date) -lt $endTime) {
    foreach ($f in $frames) {
        Write-Host "`r$f" -NoNewline
        Start-Sleep -Milliseconds 300
    }
}
Write-Host "" # ����� ������