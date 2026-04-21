import json
import os
import time
from datetime import datetime

import requests
import streamlit as st

# 页面配置
st.set_page_config(page_title="比特币价格监控", page_icon="₿", layout="centered")

# 应用标题
st.title("₿ 比特币价格监控")
st.markdown("---")

# 初始化session state
if "last_update" not in st.session_state:
    st.session_state.last_update = None
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = False
if "refresh_count" not in st.session_state:
    st.session_state.refresh_count = 0

# API配置
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/coins/markets"
COINGECKO_API_KEY_ENV = "COINGECKO_API_KEY"


def get_coingecko_api_key():
    """优先从环境变量读取 API Key，其次读取 Streamlit secrets。"""
    api_key = os.getenv(COINGECKO_API_KEY_ENV)
    if api_key:
        return api_key.strip()

    try:
        api_key = st.secrets.get(COINGECKO_API_KEY_ENV)
        if api_key:
            return api_key.strip()
    except Exception:
        pass

    return None


def build_request_headers():
    """构造请求头。"""
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }


def fetch_bitcoin_data():
    """
    从CoinGecko API获取比特币价格数据
    返回: dict包含价格和24小时变化数据，或None表示失败
    """
    try:
        api_key = get_coingecko_api_key()
        if not api_key:
            st.error(
                "未检测到 CoinGecko API Key。请设置环境变量 COINGECKO_API_KEY，"
                "或在 .streamlit/secrets.toml 中配置同名字段。"
            )
            return None

        # 设置请求参数
        params = {
            "vs_currency": "usd",
            "ids": "bitcoin",
            "price_change_percentage": "24h",
            "sparkline": "false",
            "locale": "zh",
            "x_cg_demo_api_key": api_key,
        }

        # 设置请求头
        headers = build_request_headers()

        # 发送请求
        response = requests.get(
            COINGECKO_API_URL, params=params, headers=headers, timeout=10
        )

        if response.status_code in (401, 403):
            st.error("CoinGecko API 认证失败，请检查 COINGECKO_API_KEY 是否正确。")
            return None
        if response.status_code == 429:
            st.error("CoinGecko API 请求过于频繁，请稍后再试。")
            return None

        # 检查响应状态
        response.raise_for_status()

        # 解析JSON数据
        data = response.json()

        if isinstance(data, list) and data:
            bitcoin_data = data[0]
            return {
                "usd": bitcoin_data.get("current_price"),
                "usd_24h_change": bitcoin_data.get("price_change_percentage_24h"),
                "market_cap": bitcoin_data.get("market_cap"),
                "total_volume": bitcoin_data.get("total_volume"),
                "high_24h": bitcoin_data.get("high_24h"),
                "low_24h": bitcoin_data.get("low_24h"),
                "last_updated": bitcoin_data.get("last_updated"),
            }

        st.error("CoinGecko API 返回的数据格式异常。")
        return None

    except requests.exceptions.Timeout:
        st.error("请求超时，请检查网络或稍后重试。")
        return None
    except requests.exceptions.ConnectionError as e:
        st.error(
            "无法连接 CoinGecko API。请检查当前网络是否能访问 https://api.coingecko.com。"
        )
        st.caption(f"连接错误详情: {e}")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP错误: {e.response.status_code}")
        if e.response is not None and e.response.text:
            st.caption(f"接口返回: {e.response.text[:200]}")
        return None
    except json.JSONDecodeError:
        st.error("API响应数据解析失败")
        return None
    except Exception as e:
        st.error(f"获取数据时发生未知错误: {str(e)}")
        return None


def format_price(price):
    """格式化价格显示"""
    if price is None:
        return "N/A"
    if price >= 1000:
        return f"${price:,.2f}"
    else:
        return f"${price:.2f}"


def format_change(change):
    """格式化变化百分比"""
    if change is None:
        return "N/A"

    if change > 0:
        return f"+{change:.2f}%"
    elif change < 0:
        return f"{change:.2f}%"
    else:
        return "0.00%"


def format_large_number(num):
    """格式化大数字（市值、交易量）"""
    if num is None:
        return "N/A"

    if num >= 1_000_000_000:
        return f"${num/1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"${num/1_000_000:.2f}M"
    else:
        return f"${num:,.0f}"


def display_price_card(price_data):
    """显示价格卡片"""
    if not price_data:
        return

    # 主价格显示
    current_price = price_data.get("usd")
    price_change_24h = price_data.get("usd_24h_change")

    # 创建三列布局
    col1, col2, col3 = st.columns([2, 1, 2])

    with col1:
        # 价格显示
        st.markdown(
            f"""
        <div style="text-align: center; padding: 20px; background-color: #f8f9fa;
                    border-radius: 10px; border: 1px solid #e9ecef;">
            <h3 style="color: #6c757d; margin-bottom: 10px;">当前价格</h3>
            <h1 style="color: #f7931a; font-size: 3.5rem; font-weight: bold; margin: 0;">
                {format_price(current_price)}
            </h1>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        # 24小时变化
        if price_change_24h is not None:
            change_color = "#28a745" if price_change_24h > 0 else "#dc3545"
            change_icon = "↗️" if price_change_24h > 0 else "↘️"

            # 计算涨跌额
            change_amount = (
                current_price * (price_change_24h / 100) if current_price else None
            )

            st.markdown(
                f"""
            <div style="text-align: center; padding: 20px; background-color: #f8f9fa;
                        border-radius: 10px; border: 1px solid #e9ecef;">
                <h3 style="color: #6c757d; margin-bottom: 10px;">24小时变化</h3>
                <h2 style="color: {change_color}; font-size: 2.5rem; font-weight: bold; margin: 0;">
                    {format_change(price_change_24h)}
                </h2>
                <p style="color: {change_color}; margin-top: 5px; font-size: 1.1rem;">
                    {change_icon} {format_price(change_amount) if change_amount else 'N/A'}
                </p>
            </div>
            """,
                unsafe_allow_html=True,
            )

    with col3:
        # 市场信息
        market_cap = price_data.get("market_cap")
        total_volume = price_data.get("total_volume")

        st.markdown(
            f"""
        <div style="padding: 20px; background-color: #f8f9fa;
                    border-radius: 10px; border: 1px solid #e9ecef;">
            <h3 style="color: #6c757d; margin-bottom: 15px;">市场数据</h3>
            <div style="margin-bottom: 10px;">
                <span style="color: #6c757d;">市值:</span>
                <span style="float: right; font-weight: bold;">{format_large_number(market_cap)}</span>
            </div>
            <div style="margin-bottom: 10px;">
                <span style="color: #6c757d;">24h交易量:</span>
                <span style="float: right; font-weight: bold;">{format_large_number(total_volume)}</span>
            </div>
            <div>
                <span style="color: #6c757d;">24h最高/最低:</span>
                <span style="float: right; font-weight: bold;">
                    {format_price(price_data.get('high_24h'))} / {format_price(price_data.get('low_24h'))}
                </span>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )


def main():
    """主应用函数"""

    # 侧边栏控制面板
    with st.sidebar:
        st.header("控制面板")

        # 刷新按钮
        col1, col2 = st.columns(2)
        with col1:
            refresh_clicked = st.button("🔄 刷新数据", use_container_width=True)
        with col2:
            if st.button("🔄 自动刷新", use_container_width=True):
                st.session_state.auto_refresh = not st.session_state.auto_refresh

        # 显示自动刷新状态
        if st.session_state.auto_refresh:
            st.success("自动刷新已开启 (每30秒)")
        else:
            st.info("自动刷新已关闭")

        # 刷新间隔选择
        refresh_interval = st.slider(
            "自动刷新间隔(秒)",
            min_value=10,
            max_value=120,
            value=30,
            step=10,
            disabled=not st.session_state.auto_refresh,
        )

        st.markdown("---")

        # 统计信息
        st.subheader("统计信息")
        st.write(f"刷新次数: {st.session_state.refresh_count}")
        if st.session_state.last_update:
            st.write(
                f"最后更新: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}"
            )

        st.markdown("---")

        # API状态
        st.subheader("API状态")
        api_key = get_coingecko_api_key()
        if api_key:
            st.success("已检测到 CoinGecko Demo API Key")
        else:
            st.warning("未检测到 COINGECKO_API_KEY，当前无法请求 CoinGecko API")

        st.info("使用 CoinGecko Demo API（需要 API Key）")
        if st.button("测试API连接"):
            with st.spinner("测试连接中..."):
                test_data = fetch_bitcoin_data()
                if test_data:
                    st.success("API连接正常")
                else:
                    st.error("API连接失败")

    # 主内容区域
    try:
        # 检查是否需要刷新数据
        should_refresh = (
            refresh_clicked
            or st.session_state.auto_refresh
            or st.session_state.last_update is None
            or (
                st.session_state.auto_refresh
                and (datetime.now() - st.session_state.last_update).seconds
                > refresh_interval
            )
        )

        if should_refresh:
            # 显示加载状态
            with st.spinner("正在获取比特币价格数据..."):
                # 获取数据
                price_data = fetch_bitcoin_data()

                if price_data:
                    # 更新session state
                    st.session_state.last_update = datetime.now()
                    st.session_state.refresh_count += 1

                    # 显示数据
                    display_price_card(price_data)

                    # 显示更新时间
                    st.caption(
                        f"数据更新时间: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}"
                    )

                    # 显示成功消息
                    st.success("数据更新成功！")
                else:
                    st.error("无法获取比特币价格数据，请稍后重试")

                    # 如果有旧数据，显示旧数据
                    if "last_price_data" in st.session_state:
                        st.warning("显示上次成功获取的数据")
                        display_price_card(st.session_state.last_price_data)
        else:
            # 显示缓存数据
            if "last_price_data" in st.session_state:
                display_price_card(st.session_state.last_price_data)
                if st.session_state.last_update:
                    st.caption(
                        f"数据更新时间: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    st.info("点击刷新按钮获取最新数据")
            else:
                # 首次加载
                st.info("点击刷新按钮开始获取比特币价格数据")

        # 保存数据到session state
        if "price_data" in locals() and price_data:
            st.session_state.last_price_data = price_data

    except Exception as e:
        st.error(f"应用运行时发生错误: {str(e)}")
        st.info("请尝试刷新页面或稍后重试")

    # 自动刷新逻辑
    if st.session_state.auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()


if __name__ == "__main__":
    main()
