# To run in powershell: powershell -file "C:\workspace\Agressive-Store-Bots\runner.ps1"
clear
cd C:\workspace\Agressive-Store-Bots
#docker build -t bestbuy-bot:latest .
docker compose down
docker compose up -d
docker logs -f bestbuy-bot