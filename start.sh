#!/bin/bash

echo "正在启动后端服务器..."
cd backend
python -m src.garden_link &
BACKEND_PID=$!
cd ..

sleep 3

echo "正在启动前端开发服务器..."
cd frontend
bun run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "=== 服务已启动 ==="
echo "后端: http://localhost:8908"
echo "前端: http://localhost:8918"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo ""

# 等待用户中断
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
