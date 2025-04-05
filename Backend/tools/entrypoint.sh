#!/bin/bash

# COLORS
BL='\033[0;36m'
GR='\033[0;32m'
NC='\033[0m'

cd /app

# Apply database migrations
echo -e $BL 'Starting 'python manage.py makemigrations'...' $NC > migration_logs.log
python manage.py makemigrations >> migration_logs.log
echo -e $BL 'Starting 'python manage.py makemigrations'...' $GR 'DONE' $NC >> migration_logs.log
echo -e $BL '================================================'$NC >> migration_logs.log

echo -e $BL 'Starting 'python manage.py migrate'...'$NC >> migration_logs.log
python manage.py migrate >> migration_logs.log
echo -e $BL 'Starting 'python manage.py migrate'...' $GR 'DONE' $NC >> migration_logs.log
echo -e $BL '================================================' $NC >> migration_logs.log

cat migration_logs.log

echo -e $BL 'Start setupTranslation.sh...' $NC
# python manage.py makemessages -l en_US -l pt_PT -l pt_BR -l de_DE -l uk_UA -l ne_NP
python manage.py compilemessages
echo -e $BL 'Start setupTranslation.sh...' $GR 'DONE' $NC
echo -e $BL '================================================' $NC

echo -e $BL '================================================' $NC
echo -e "${BL}Running Celery as appuser...${NC}"
export > /home/appuser/.tempEnv
sleep 1
su - appuser -c "
source /home/appuser/.tempEnv && celery -A app worker --loglevel=warning &
source /home/appuser/.tempEnv && celery -A app beat --loglevel=warning &
" &
echo -e "${BL}Running Celery as appuser...${GR}DONE${NC}"
echo -e $BL '================================================' $NC

echo -e $BL 'Starting Server...' $NC
exec "$@"