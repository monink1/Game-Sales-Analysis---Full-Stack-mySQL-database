# 第一阶段：构建前端项目（使用 Node 环境编译代码）
FROM node:20-alpine as build-stage
WORKDIR /app

# 复制依赖配置文件
COPY package*.json ./

# 安装项目依赖
RUN npm install

# 复制所有项目文件到容器内
COPY . .

# 构建生产环境代码（生成 dist 目录）
RUN npm run build


# 第二阶段：部署前端项目（使用 Nginx 运行静态文件）
FROM nginx:alpine as production-stage

# 复制构建阶段生成的 dist 目录到 Nginx 静态文件目录
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 可选：如果需要解决 Vue Router history 模式刷新 404 问题，取消下面两行注释
# 注意：需在前端项目根目录创建 nginx.conf 文件（内容见说明）
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露容器的 80 端口（Nginx 默认端口）
EXPOSE 80

# 启动 Nginx 服务（前台运行，确保容器不退出）
CMD ["nginx", "-g", "daemon off;"]
