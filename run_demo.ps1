# -------------------------
# Скрипт для тестовой email-рассылки
# -------------------------

# 1️⃣ Получаем токен для admin
$login = @{
    username = "admin"
    password = "admin"
} | ConvertTo-Json

$response = curl -X POST "http://127.0.0.1:8000/auth/login" `
    -H "Content-Type: application/json" `
    -d $login

$token = ($response | ConvertFrom-Json).access_token
Write-Host "Получен токен:" $token

# 2️⃣ Создаём шаблон письма
$response_template = curl -X POST "http://127.0.0.1:8000/templates/" `
    -H "Content-Type: application/json" `
    -H ("token: " + $token) `
    -d (Get-Content -Raw template.json)

$template_id = ($response_template | ConvertFrom-Json).id
Write-Host "Создан шаблон с ID:" $template_id

# 3️⃣ Создаём кампанию (обновляем template_id в JSON)
$campaign = Get-Content -Raw campaign.json | ConvertFrom-Json
$campaign.template_id = $template_id
$campaign_json = $campaign | ConvertTo-Json -Compress

$response_campaign = curl -X POST "http://127.0.0.1:8000/campaigns/" `
    -H "Content-Type: application/json" `
    -H ("token: " + $token) `
    -d $campaign_json

$campaign_id = ($response_campaign | ConvertFrom-Json).id
Write-Host "Создана кампания с ID:" $campaign_id

# 4️⃣ Запускаем кампанию немедленно
$response_start = curl -X POST ("http://127.0.0.1:8000/campaigns/" + $campaign_id + "/start_now") `
    -H ("token: " + $token)

Write-Host "Результат запуска кампании:" $response_start
