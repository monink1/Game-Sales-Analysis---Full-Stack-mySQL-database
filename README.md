A full-stack data visualization application focused on game sales data, built for graduate course assignment. The app supports multi-dimensional data analysis and visualization, demonstrating efficient database modeling and standard software engineering practices.

用了anaconda创建的虚拟环境，前端后端的都在requirements.txt,然后dorcker desktop下载nodejs，python用flask框架，mysql导入的是https://www.kaggle.com/datasets/gregorut/videogamesales?resource=download的数据集，之后稍微后处理了五个接口，本地可以显示其效果。勉勉强强算全栈数据库吧。


📋 Project Overview
This project is a full-stack application centered around game sales data (from global game market datasets). It solves the problem of "multi-dimensional game sales analysis" for game publishers, investors, and market researchers by providing intuitive data visualization and query capabilities.

Core value:
Analyze top-selling games and market share of platforms/regions
Identify core products of leading publishers
Support data-driven decisions in the game industry
✨ Key Features
Feature	Description	Visualization Type
Global Top 10 Games	Display the top 10 best-selling games worldwide (sorted by global sales)	Interactive Table
Platform Sales Distribution	Analyze total sales of each gaming platform (e.g., PS2, Wii, X360)	Bar Chart
Regional Sales Proportion	Show sales share across regions (North America, Europe, Japan, Others)	Donut Chart
PC Platform Top 20	Focus on top 20 best-selling games on PC platform	Interactive Table
Top 5 Publishers' Core Games	Visualize sales proportion of top 3 games for each of the top 5 publishers	5 Donut Charts
🛠️ Tech Stack
Layer	Technologies	Version
Frontend	Vue.js	3.x
Vite	4.x
ECharts	5.x
Axios	1.x
Vue Router	4.x
Backend	Flask	2.x
Flask-SQLAlchemy	3.x
Flask-CORS	4.x
Database	MySQL	8.0
Deployment	Docker	24.x
Docker Compose	2.x
