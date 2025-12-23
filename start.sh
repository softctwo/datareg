#!/bin/bash
# 系统启动脚本
# 作者：张彦龙

echo "========================================"
echo "启动银行重要数据跨境数据管控系统"
echo "========================================"
echo ""

# 检查数据库
echo "检查数据库连接..."
cd "$(dirname "$0")/backend"
python3 -c "from app.core.database import SessionLocal; db = SessionLocal(); print('✅ 数据库连接正常'); db.close()" 2>&1
if [ $? -ne 0 ]; then
    echo "❌ 数据库连接失败，请检查PostgreSQL服务"
    exit 1
fi

# 启动后端服务
echo ""
echo "启动后端服务..."
cd "$(dirname "$0")/backend"
nohup uvicorn app.main:app --reload --port 8000 > /tmp/datareg_backend.log 2>&1 &
BACKEND_PID=$!
echo "后端服务PID: $BACKEND_PID"
sleep 3

# 检查后端服务
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 后端服务启动成功 (http://localhost:8000)"
else
    echo "❌ 后端服务启动失败，查看日志: /tmp/datareg_backend.log"
    exit 1
fi

# 启动前端服务
echo ""
echo "启动前端服务..."
cd "$(dirname "$0")/frontend"
nohup npm run dev > /tmp/datareg_frontend.log 2>&1 &
FRONTEND_PID=$!
echo "前端服务PID: $FRONTEND_PID"
sleep 5

# 检查前端服务
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ 前端服务启动成功 (http://localhost:3000)"
else
    echo "⚠️  前端服务可能还在启动中，请稍候..."
fi

echo ""
echo "========================================"
echo "✅ 系统启动完成！"
echo "========================================"
echo ""
echo "🌐 访问地址："
echo "   前端: http://localhost:3000"
echo "   后端: http://localhost:8000"
echo "   API文档: http://localhost:8000/api/docs"
echo ""
echo "🔑 默认登录账号："
echo "   管理员: admin / admin123"
echo "   测试用户: test / test123"
echo ""
echo "📝 日志文件："
echo "   后端: /tmp/datareg_backend.log"
echo "   前端: /tmp/datareg_frontend.log"
echo ""
echo "🛑 停止服务："
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
