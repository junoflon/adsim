"""
MiroFish Backend 启动入口
"""

import os
import sys

# 解决 Windows 控制台中文乱码问题：在所有导入之前设置 UTF-8 编码
if sys.platform == 'win32':
    # 设置环境变量确保 Python 使用 UTF-8
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    # 重新配置标准输出流为 UTF-8
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.config import Config


def main():
    """主函数"""
    # 验证配置
    errors = Config.validate()
    if errors:
        print("配置错误:")
        for err in errors:
            print(f"  - {err}")
        print("\n请检查 .env 文件中的配置")
        sys.exit(1)
    
    # 创建应用
    app = create_app()
    
    # 获取运行配置
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5001))
    # Railway(프로덕션)에선 debug 강제 비활성화 — 리로더가 백그라운드 스레드를 죽이는 문제 방지
    is_railway = bool(os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RAILWAY_SERVICE_ID'))
    flask_debug_env = os.environ.get('FLASK_DEBUG', '').lower()
    if is_railway or flask_debug_env == 'false':
        debug = False
    else:
        debug = Config.DEBUG

    # 启动服务
    app.run(host=host, port=port, debug=debug, threaded=True, use_reloader=debug)


if __name__ == '__main__':
    main()

