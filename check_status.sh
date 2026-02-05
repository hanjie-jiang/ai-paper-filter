#!/bin/bash
# Quick status checker

echo "Process status:"
if ps aux | grep "main.py" | grep -v grep > /dev/null; then
    echo "  RUNNING"
    ps aux | grep "main.py" | grep -v grep | awk '{print "  CPU: " $3 "% | Memory: " $6/1024 " MB"}'
else
    echo "  COMPLETED or STOPPED"
fi

echo ""
echo "Output files:"
ls -lh output/*.html output/*.json 2>/dev/null || echo "  No output files yet"

echo ""
echo "To see full log, run: tail -50 /tmp/claude/-Users-hanjiang-Desktop-local-code-ai-paper-filter/tasks/b8bb8af.output"
