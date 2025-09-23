# Author: shen weijie
# Date: 2025-08-28
# Description: 淘宝商品数据分析
#----------------------
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import re
import os
import time

# 添加pyecharts导入
from pyecharts.charts import Map
from pyecharts import options as opts   
from pyecharts.charts import Geo
from streamlit_echarts import st_pyecharts
from pyecharts.globals import ChartType  

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 设置页面配置
st.set_page_config(
    page_title="淘宝商品数据分析",
    page_icon="🛍️",
    layout="wide"
)

# 读取Excel数据
@st.cache_data
def load_data(file_path):
    df = pd.read_excel(file_path)
    # 数据清洗
    df = clean_price_data(df)
    df = clean_sales_data(df)
    df = extract_province_data(df)
    return df

def clean_price_data(df):
    """清洗价格数据"""
    df['价格'] = df['价格'].astype(str).apply(lambda x: re.findall(r'\d+\.?\d*', x))
    df['价格'] = df['价格'].apply(lambda x: float(x[0]) if len(x) > 0 else 0)
    return df

def clean_sales_data(df):
    """清洗交易数量数据"""
    def extract_sales(sales_str):
        sales_str = str(sales_str)
        # 处理"万+"格式
        if '万' in sales_str:
            num = re.findall(r'\d+\.?\d*', sales_str)
            if num:
                return float(num[0]) * 10000
        else:
            num = re.findall(r'\d+', sales_str)
            if num:
                return float(num[0])
        return 0
    
    df['交易数量'] = df['交易数量'].apply(extract_sales)
    return df

def extract_province_data(df):
    """提取省份数据"""
    df['省份'] = df['店铺所在地'].astype(str).apply(lambda x: x.split()[0] if x else "未知")
    return df

def display_data_overview(df):
    """显示数据概览"""
    st.header("📊 数据概览")
    col1, col2, col3 = st.columns(3)
    col1.metric("商品总数", len(df))
    col2.metric("平均价格", f"¥{df['价格'].mean():.2f}")
    col3.metric("总交易量", int(df['交易数量'].sum()))
    
    st.dataframe(df.head(10), use_container_width=True)

def plot_price_distribution(df):
    """绘制价格分布图"""
    st.header("💰 价格分布分析")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(data=df, x='价格', bins=30, kde=True, ax=ax)
    ax.set_title('商品价格分布直方图')
    ax.set_xlabel('价格 (元)')
    ax.set_ylabel('商品数量')
    st.pyplot(fig)

def plot_top_sales(df):
    """绘制交易量前20商品图"""
    st.header("📈 交易数量分析")
    fig, ax = plt.subplots(figsize=(10, 6))
    # 取交易量前20的商品
    top_sales = df.nlargest(20, '交易数量')
    sns.barplot(data=top_sales, x='交易数量', y='商品简介', ax=ax)
    ax.set_title('交易量前20商品')
    ax.set_xlabel('交易数量')
    ax.set_ylabel('商品名称')
    st.pyplot(fig)

def plot_province_distribution(df):
    """绘制店铺所在地分布图（饼图）"""
    st.header("📍 店铺所在地分析")
    province_counts = df['省份'].value_counts().head(15)
    
    # 创建饼图
    fig, ax = plt.subplots(figsize=(12, 8))
    wedges, texts, autotexts = ax.pie(
        province_counts.values, 
        labels=province_counts.index, 
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 10}
    )
    
    # 设置标题
    ax.set_title('店铺所在地分布 (前15省)', fontsize=16, pad=20)
    
    # 美化饼图标签
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    # 添加图例
    ax.legend(wedges, province_counts.index, title="省份", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    
    st.pyplot(fig)

def normalize_province_names(province_counts):
    """规范化省份名称，确保省名加'省'，市名加'市'"""
    # 定义直辖市
    municipalities = ['北京', '天津', '上海', '重庆']
    # 定义特别行政区
    special_admin_regions = ['香港', '澳门']
    # 定义自治区
    autonomous_regions = {
        '内蒙古': '内蒙古自治区',
        '广西': '广西壮族自治区',
        '西藏': '西藏自治区',
        '宁夏': '宁夏回族自治区',
        '新疆': '新疆维吾尔自治区'
    }
    
    normalized_data = []
    
    for _, row in province_counts.iterrows():
        province = row['省份']
        count = row['店铺数量']
        
        # 处理直辖市
        if province in municipalities:
            normalized_province = province + '市'
        # 处理特别行政区
        elif province in special_admin_regions:
            normalized_province = province + '特别行政区'
        # 处理自治区
        elif province in autonomous_regions:
            normalized_province = autonomous_regions[province]
        # 处理普通省份
        elif not province.endswith(('省', '市', '自治区', '特别行政区')):
            normalized_province = province + '省'
        else:
            normalized_province = province
            
        normalized_data.append({'省份': normalized_province, '店铺数量': count})
    
    return pd.DataFrame(normalized_data)

def plot_province_map(df):
    """绘制店铺所在地地图
       pyecharts 地图无法显示通常是因为缺少相应的地图数据包。请确保你已经安装了 echarts-china-provinces-pypkg 包。
       可以使用以下命令安装：
       pip install echarts-countries-pypkg
       pip install echarts-china-provinces-pypkg
       pip install echarts-china-cities-pypkg
       pip install echarts-china-counties-pypkg
    """
    st.header("🗺️ 店铺所在地地图")
    # 统计各省份的店铺数量
    province_counts = df['省份'].value_counts().reset_index()
    province_counts.columns = ['省份', '店铺数量']
    
    # 规范化省份名称
    province_counts = normalize_province_names(province_counts)
        
    # 准备地图数据
    provinces = province_counts['省份'].tolist()
    shop_counts = province_counts['店铺数量'].tolist()
    
    # 获取最大值以设置 visualmap
    max_count = max(shop_counts) if shop_counts else 100
    
    # 创建 Map 图表，并设置尺寸为最大化显示
    map_chart = Map(init_opts=opts.InitOpts(width="100%", height="800px"))

    # 合并各省数据将provinces和shop_counts整合成一个data  
    data = list(zip(provinces, shop_counts))

    # 启用缩放功能 (is_roam=True)
    map_chart.add("店铺数量", data, "china", is_roam=True)  # 注意这里的 maptype 是 "china"
    
    # 设置全局选项
    map_chart.set_global_opts(
        title_opts=opts.TitleOpts(title="店铺数量分布图"),
        visualmap_opts=opts.VisualMapOpts(
            max_=max_count,
            is_piecewise=True,
            pieces=[
                {"min": 0, "max": max_count//10, "label": f"0-{max_count//10}", "color": "#FFE4E1"},
                {"min": max_count//10+1, "max": max_count//5, "label": f"{max_count//10+1}-{max_count//5}", "color": "#FF7F50"},
                {"min": max_count//5+1, "max": max_count//2, "label": f"{max_count//5+1}-{max_count//2}", "color": "#FF4500"},
                {"min": max_count//2+1, "max": max_count, "label": f"{max_count//2+1}-{max_count}", "color": "#FF0000"},
            ]
        )
    )
    
    # 渲染地图
    map_chart.render("province_map.html")
    
    # 读取渲染后的 HTML 文件
    with open("province_map.html", "r", encoding="utf-8") as f:
        map_html = f.read()
    
    # 显示地图
    st.components.v1.html(map_html, width=1200, height=800)

def plot_price_sales_relationship(df):
    """绘制价格与交易量关系图"""
    st.header("🔗 价格与交易量关系")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=df, x='价格', y='交易数量', ax=ax)
    ax.set_title('价格与交易量散点图')
    ax.set_xlabel('价格 (元)')
    ax.set_ylabel('交易数量')
    st.pyplot(fig)

def plot_shop_analysis(df):
    """绘制店铺分析图"""
    st.header("🏪 店铺分析")
    shop_stats = df.groupby('店铺名称').agg({
        '价格': 'mean',
        '交易数量': 'sum'
    }).round(2)
    shop_stats = shop_stats.sort_values('交易数量', ascending=False).head(15)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=shop_stats['交易数量'], y=shop_stats.index, ax=ax)
    ax.set_title('店铺总交易量排行 (前15)')
    ax.set_xlabel('总交易量')
    ax.set_ylabel('店铺名称')
    st.pyplot(fig)

def display_data_statistics(df):
    """显示数据统计信息"""
    st.header("📈 数据统计")
    st.subheader("价格统计")
    st.write(df['价格'].describe())
    
    st.subheader("交易量统计")
    st.write(df['交易数量'].describe())

def display_data_filter(df):
    """显示数据筛选功能"""
    st.header("🔍 数据筛选")
    st.markdown("### 按价格筛选")
    min_price, max_price = st.slider(
        "选择价格区间 (元)", 
        float(df['价格'].min()), 
        float(df['价格'].max()), 
        (float(df['价格'].min()), float(df['价格'].max()))
    )
    
    filtered_df = df[(df['价格'] >= min_price) & (df['价格'] <= max_price)]
    
    st.markdown(f"### 筛选结果 (价格在 {min_price:.2f} - {max_price:.2f} 元之间)")
    st.dataframe(filtered_df[['商品简介', '价格', '交易数量', '店铺名称']], use_container_width=True)

# 主函数
def main():
    st.title("🛍️ 淘宝商品数据分析展示")
    st.markdown("---")
    
    # 创建侧边栏
    st.sidebar.title("数据查看")
    
    # 侧边栏选项
    show_data_overview = st.sidebar.checkbox("数据概览", value=True)
    show_price_analysis = st.sidebar.checkbox("价格分析", value=True)
    show_sales_analysis = st.sidebar.checkbox("交易量分析", value=True)
    show_location_analysis = st.sidebar.checkbox("位置分析", value=True)
    show_relationship_analysis = st.sidebar.checkbox("关系分析", value=True)
    show_shop_analysis = st.sidebar.checkbox("店铺分析", value=True)
    show_data_statistics = st.sidebar.checkbox("数据统计", value=True)
    show_data_filter = st.sidebar.checkbox("数据筛选", value=True)
    
    # 获取当前脚本的绝对路径
    script_path = os.path.abspath(__file__)    
    # 获取脚本所在的目录
    current_directory = os.path.dirname(script_path)    
    #保存文件名
    data_file = f'{current_directory}/output/fetch_taobao_2025.xlsx'    

    try:
        df = load_data(data_file)
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return
    
    # 根据侧边栏选项显示内容
    if show_data_overview:
        # 显示数据概览
        display_data_overview(df)
    
    if show_price_analysis or show_sales_analysis:
        col1, col2 = st.columns(2)
        with col1:
            # 价格分布分析
            if show_price_analysis:
                plot_price_distribution(df)
        with col2:
            # 交易数量分析
            if show_sales_analysis:
                plot_top_sales(df)
    
    if show_location_analysis:
        # 店铺所在地分析
        col3, col4 = st.columns(2)
        with col3:
            plot_province_distribution(df)
        with col4:
            plot_province_map(df)
    
    if show_relationship_analysis or show_shop_analysis:
        col5, col6 = st.columns(2)
        with col5:
            # 价格与交易量关系
            if show_relationship_analysis:
                plot_price_sales_relationship(df)
        with col6:
            # 店铺分析
            if show_shop_analysis:
                plot_shop_analysis(df)
    
    if show_data_statistics or show_data_filter:
        col7, col8 = st.columns(2)
        with col7:
            # 数据统计
            if show_data_statistics:
                display_data_statistics(df)
        with col8:
            # 高级筛选
            if show_data_filter:
                display_data_filter(df)

if __name__ == "__main__":
    main()
