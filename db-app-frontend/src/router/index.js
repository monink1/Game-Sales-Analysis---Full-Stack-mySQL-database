import { createRouter, createWebHistory } from 'vue-router';
// 导入业务页面组件（确保路径和你的实际文件位置一致）
import SalesAnalysis from '../views/SalesAnalysis.vue';

// 路由规则：定义路径和对应组件的映射
const routes = [
  {
    path: '/',  // 根路径（首页）
    name: 'SalesAnalysis',  // 路由名称（可选）
    component: SalesAnalysis  // 对应显示的组件
  }
];

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),  // 使用HTML5 history模式（无#号）
  routes  // 应用路由规则
});

export default router;
    