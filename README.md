## Project Overview
First, use Selenium to automatically scrape product information from Taobao and JD for the same items. Then, process and clean the collected data. Next, analyze the same products based on indicators such as price, sales volume . Finally, use tools like Seaborn, Pyecharts, and Streamlit to visualize and display the comparison differences

## Main Features
### 1.Data-crawling module: uses Selenium to drive the browser automatically and locates key elements such as price and sales volume on Taobao/JD product pages via XPath.
### 2.Data-cleaning module: deduplicates the raw data, handles missing values, and standardizes formats (e.g., unifying currency units).
### 3.Analysis & comparison module: calculates the price-gap percentage for the same product across the two platforms, and summarizes sales-volume distribution and origin concentration.
### 4.Visualization module: generates statistical distribution plots with Seaborn and produces interactive comparison bar charts with Pyecharts.
### 5.Interactive interface: a Streamlit-powered dashboard that lets users filter product categories and choose sorting dimensions.
