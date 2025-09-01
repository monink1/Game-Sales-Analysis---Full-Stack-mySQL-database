### Abstract:

A full-stack data visualization application focused on game sales data, built for graduate course assignment. The app supports multi-dimensional data analysis and visualization, demonstrating efficient database modeling and standard software engineering practices.



### 部署复现流程：

mysql导入的是

```website
https://www.kaggle.com/datasets/gregorut/videogamesales?resource=download
```

的数据集，之后稍微后处理了五个接口，本地可以显示其效果。勉勉强强算全栈数据库吧。



1.下载mysql(包括workbench),anaconda,docker desktop.



2.安装anaconda虚拟环境依赖（requirements.txt）

创建环境python=3.10



3.下载node.js 

```website
https://nodejs.org/zh-cn/download/archive/v20.19.4
```

解压后路径添加到环境变量



4.vue3创建

```cmd
npm create vue@latest db-app-frontend


cd db-app-frontend

npm install element-plus @element-plus/icons-vue

npm run dev
```



5.dorker desktop 

setting -> docker engine 改成

```
{
  "experimental": false,
  "features": {
    "buildkit": true
  },
  "registry-mirrors": [
    "https://hub-mirror.c.163.com",
    "https://mirror.ccs.tencentyun.com"
  ]
}

```

6.docker-compose.yml是关键，在docker-test里面



7.连接mysql端口什么的确认完整，我是3307。导入操作保证句句正确，这里注意CSV要再次保存确认是UTF-8格式，不然导入有很多报错。



8.进入 docker-test 目录

```
cd E:\node\docker-test
```



重新构建并启动所有服务（--build 确保用最新配置）

```
docker compose up -d --build
```

再次查看服务状态，确认 backend-test 出现

```
docker compose ps
```

有如下：

```
(data) E:\node\docker-test>docker compose ps
NAME            IMAGE                       COMMAND                   SERVICE         CREATED          STATUS                   PORTS
flask-backend   docker-test-backend-test    "python app.py"           backend-test    14 minutes ago   Up 5 minutes             0.0.0.0:5000->5000/tcp, [::]:5000->5000/tcp
mysql-db        mysql:8.0                   "docker-entrypoint.s…"   mysql-test      27 minutes ago   Up 5 minutes (healthy)   0.0.0.0:3307->3306/tcp, [::]:3307->3306/tcp
vue-frontend    docker-test-frontend-test   "/docker-entrypoint.…"   frontend-test   14 minutes ago   Up 5 minutes             0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
```

三个都存在则说明互相已经连接上





### 部署完成后再次开启：

开启docker desktop,anaconda激活环境

docker compose up -d --build

然后查看
http://localhost:8080/
即可

#### 📋 Project Overview

This project is a full-stack application centered around game sales data (from global game market datasets). It solves the problem of "multi-dimensional game sales analysis" for game publishers, investors, and market researchers by providing intuitive data visualization and query capabilities.

Core value:
Analyze top-selling games and market share of platforms/regions
Identify core products of leading publishers
Support data-driven decisions in the game industry

#### ✨ Key Features

Feature	Description	Visualization Type
Global Top 10 Games	Display the top 10 best-selling games worldwide (sorted by global sales)	Interactive Table
Platform Sales Distribution	Analyze total sales of each gaming platform (e.g., PS2, Wii, X360)	Bar Chart
Regional Sales Proportion	Show sales share across regions (North America, Europe, Japan, Others)	Donut Chart
PC Platform Top 20	Focus on top 20 best-selling games on PC platform	Interactive Table
Top 5 Publishers' Core Games	Visualize sales proportion of top 3 games for each of the top 5 publishers	5 Donut Charts

#### 🛠️ Tech Stack

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
