Set-Location $PSScriptRoot/../src
$Env:FLASK_APP = 'olea'
$Env:FLASK_ENV = 'dev'
flask init-db
