#!/bin/bash

# 钛合金数据转换器启动脚本

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Python环境
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        log_error "未找到Python环境，请先安装Python 3.6+"
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    log_info "使用Python版本: $PYTHON_VERSION"
}

# 检查依赖
check_dependencies() {
    log_info "检查Python依赖..."
    
    # 检查pandas
    if $PYTHON_CMD -c "import pandas" 2>/dev/null; then
        log_success "pandas 已安装"
    else
        log_warning "pandas 未安装，尝试安装..."
        pip install pandas
        if [ $? -ne 0 ]; then
            log_error "pandas 安装失败"
            exit 1
        fi
    fi
    
    # 检查其他依赖
    for package in numpy python-dateutil pytz six; do
        if $PYTHON_CMD -c "import $package" 2>/dev/null; then
            log_success "$package 已安装"
        else
            log_warning "$package 未安装"
        fi
    done
}

# 检查配置文件
check_config() {
    if [ ! -f "config.json" ]; then
        log_error "配置文件 config.json 不存在"
        exit 1
    fi
    
    # 检查输入文件是否存在
    INPUT_CSV=$(python3 -c "import json; print(json.load(open('config.json'))['input_csv'])" 2>/dev/null)
    if [ ! -f "$INPUT_CSV" ]; then
        log_error "输入文件不存在: $INPUT_CSV"
        log_info "请修改 config.json 中的 input_csv 路径"
        exit 1
    fi
    
    log_success "配置文件检查通过"
    log_info "输入文件: $INPUT_CSV"
}

# 运行测试
run_tests() {
    log_info "运行功能测试..."
    
    if $PYTHON_CMD test_conversion.py; then
        log_success "功能测试通过"
    else
        log_warning "功能测试发现一些问题，但将继续执行转换"
    fi
}

# 执行转换
run_conversion() {
    log_info "开始数据转换..."
    
    START_TIME=$(date +%s)
    
    if $PYTHON_CMD convert_ti_data.py; then
        END_TIME=$(date +%s)
        DURATION=$((END_TIME - START_TIME))
        
        # 获取输出文件信息
        OUTPUT_FILE=$(python3 -c "import json; print(json.load(open('config.json'))['output_jsonl'])" 2>/dev/null)
        
        if [ -f "$OUTPUT_FILE" ]; then
            FILE_SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
            LINE_COUNT=$(wc -l < "$OUTPUT_FILE")
            
            log_success "转换完成！"
            log_info "输出文件: $OUTPUT_FILE"
            log_info "文件大小: $FILE_SIZE"
            log_info "记录数量: $LINE_COUNT"
            log_info "处理时间: ${DURATION}秒"
            
            # 显示前3条记录作为示例
            log_info "前3条记录示例:"
            head -n 3 "$OUTPUT_FILE" | $PYTHON_CMD -m json.tool
        else
            log_error "输出文件未生成"
            exit 1
        fi
    else
        log_error "转换过程失败"
        exit 1
    fi
}

# 显示使用说明
show_usage() {
    echo -e "${BLUE}钛合金数据转换器使用说明${NC}"
    echo ""
    echo "功能: 将钛合金CSV数据转换为JSONL格式，适用于大模型检索增强生成任务"
    echo ""
    echo "使用方法:"
    echo "  ./run_conversion.sh          # 执行完整转换流程"
    echo "  ./run_conversion.sh test     # 仅运行测试"
    echo "  ./run_conversion.sh config   # 仅检查配置"
    echo ""
    echo "文件说明:"
    echo "  convert_ti_data.py    - 主转换脚本"
    echo "  text_generator.py     - 文本生成模块"
    echo "  config.json          - 配置文件"
    echo "  test_conversion.py    - 测试脚本"
    echo "  README.md            - 详细说明文档"
    echo ""
}

# 主函数
main() {
    echo -e "${BLUE}=== 钛合金数据转换器 ===${NC}"
    echo ""
    
    # 解析参数
    case "$1" in
        "test")
            check_python
            run_tests
            ;;
        "config")
            check_python
            check_config
            ;;
        ""|"full")
            check_python
            check_dependencies
            check_config
            run_tests
            run_conversion
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            log_error "未知参数: $1"
            show_usage
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"