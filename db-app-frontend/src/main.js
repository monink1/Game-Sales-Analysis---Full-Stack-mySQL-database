import { createApp } from 'vue';
import App from './App.vue';
// 引入路由配置
import router from './router';

// 创建应用实例，使用路由插件，挂载到#app
createApp(App)
  .use(router)  // 注册路由
  .mount('#app');
    