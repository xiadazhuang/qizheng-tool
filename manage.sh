#!/bin/bash
case "$1" in
  start)
    cd ~/qizheng-tool
    python3 -m streamlit run src/web_app.py --server.port 8501 &
    echo "Started"
    ;;
  stop)
    pkill -f "streamlit run.*web_app.py"
    echo "Stopped"
    ;;
  status)
    curl -s --max-time 2 http://localhost:8501 > /dev/null && echo "Running" || echo "Stopped"
    ;;
  restart)
    $0 stop
    sleep 1
    $0 start
    ;;
  *)
    echo "Usage: manage.sh {start|stop|status|restart}"
    ;;
esac
