<template>
  <div class="analysis-container">
    <!-- 页面标题 -->
    <h1 class="page-title">游戏销量数据分析</h1>

    <!-- 1. 全球销量Top10表格 -->
    <div class="data-card">
      <h2 class="card-title">全球销量Top10游戏</h2>
      <div class="table-wrapper">
        <table class="sales-table">
          <thead>
            <tr>
              <th>排名</th>
              <th>游戏名称</th>
              <th>平台</th>
              <th>全球销量（百万）</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="game in topGames" :key="game.Rank">
              <td class="rank-cell">{{ game.Rank }}</td>
              <td class="name-cell">{{ game.Name }}</td>
              <td class="platform-cell">{{ game.Platform }}</td>
              <td class="sales-cell">{{ game.Global_Sales.toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 2. 平台销量柱状图 -->
    <div class="data-card">
      <h2 class="card-title">各平台总销量分布</h2>
      <div ref="platformChart" class="chart-container"></div>
    </div>

    <!-- 3. 地区销量饼图 -->
    <div class="data-card">
      <h2 class="card-title">各地区销量占比</h2>
      <div ref="regionChart" class="chart-container"></div>
    </div>

    <!-- 4. PC端游戏销量Top20 -->
    <div class="data-card">
      <h2 class="card-title">PC端游戏销量Top20</h2>
      <div class="table-wrapper">
        <table class="sales-table">
          <thead>
            <tr>
              <th>排名</th>
              <th>游戏名称</th>
              <th>发行商</th>
              <th>全球销量（百万）</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(game, index) in pcTop20" :key="index">
              <td class="rank-cell">{{ index + 1 }}</td>
              <td class="name-cell">{{ game.Name }}</td>
              <td class="publisher-cell">{{ game.Publisher }}</td>
              <td class="sales-cell">{{ game.Global_Sales.toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 5. 前十发行商的Top3游戏饼图 -->
    <div class="data-card">
      <h2 class="card-title">前十畅销发行商的Top3游戏销量占比</h2>
      <div class="publishers-grid">
        <!-- 使用函数式ref将容器存入数组 -->
        <div v-for="(publisher, index) in top10Publishers" :key="publisher.publisher" class="publisher-item">
          <h3 class="publisher-title">{{ index + 1 }}. {{ publisher.publisher }}</h3>
          <!-- 函数式ref：直接将当前元素存入数组的对应索引 -->
          <div :ref="(el) => publisherChartRefs[index] = el" class="small-chart-container"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue';
import axios from 'axios';
import * as echarts from 'echarts';

// 响应式数据存储
const topGames = ref([]);
const platformData = ref({ platforms: [], total_sales: [] });
const regionData = ref([]);
const pcTop20 = ref([]);
const topPublishers = ref([]);

// 计算属性：取前10个发行商
const top10Publishers = computed(() => topPublishers.value.slice(0, 10));

// 图表容器引用
const platformChart = ref(null);
const regionChart = ref(null);
// 用数组存储容器（索引对应发行商顺序）
const publisherChartRefs = ref([]); 

// 页面加载时获取数据并初始化图表
onMounted(async () => {
  try {
    // 并行请求接口
    const [topRes, platformRes, regionRes, pcRes, publisherRes] = await Promise.all([
      axios.get('http://localhost:5000/api/sales/top?n=10'),
      axios.get('http://localhost:5000/api/sales/by-platform'),
      axios.get('http://localhost:5000/api/sales/by-region'),
      axios.get('http://localhost:5000/api/sales/pc-top20'),
      axios.get('http://localhost:5000/api/sales/top-publishers') // 获取全部发行商数据
    ]);

    // 存储数据
    topGames.value = topRes.data.data;
    platformData.value = platformRes.data.data;
    regionData.value = regionRes.data.data;
    pcTop20.value = pcRes.data.data || [];
    topPublishers.value = publisherRes.data.data || [];

    // 等待DOM渲染完成
    await nextTick();
    
    // 初始化图表
    initPlatformChart();
    initRegionChart();
    initPublisherCharts();

  } catch (error) {
    console.error('数据加载失败:', error);
    alert('数据加载失败，请检查后端服务是否正常');
  }
});

// 初始化平台销量柱状图
const initPlatformChart = () => {
  if (!platformChart.value || platformData.value.platforms.length === 0) {
    console.warn('平台图表容器不存在或数据为空');
    return;
  }

  const chart = echarts.init(platformChart.value);
  chart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: '{b}: {c} 百万'
    },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: {
      type: 'category',
      data: platformData.value.platforms,
      axisLabel: { rotate: 45, interval: 0, fontSize: 12 }
    },
    yAxis: { type: 'value', name: '总销量（百万）' },
    series: [{
      name: '销量',
      type: 'bar',
      data: platformData.value.total_sales,
      itemStyle: {
        color: (params) => params.dataIndex < 3 
          ? ['#f56c6c', '#e6a23c', '#409eff'][params.dataIndex] 
          : '#67c23a'
      },
      label: { show: true, position: 'top', fontSize: 10 }
    }]
  });

  window.addEventListener('resize', () => chart.resize());
};

// 初始化地区销量饼图
const initRegionChart = () => {
  if (!regionChart.value || regionData.value.length === 0) {
    console.warn('地区图表容器不存在或数据为空');
    return;
  }

  const chart = echarts.init(regionChart.value);
  chart.setOption({
    tooltip: { trigger: 'item', formatter: '{a} <br/>{b}: {c} 百万 ({d}%)' },
    legend: { orient: 'horizontal', bottom: 0, itemWidth: 12, itemHeight: 12 },
    series: [{
      name: '地区销量',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '40%'],
      itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
      data: regionData.value.map(item => ({ name: item.region, value: item.sales }))
    }]
  });

  window.addEventListener('resize', () => chart.resize());
};

// 初始化发行商Top3游戏饼图
const initPublisherCharts = () => {
  // 打印容器数组，方便调试
  console.log('发行商图表容器数组:', publisherChartRefs.value);

  // 遍历前10个发行商
  top10Publishers.value.forEach((publisher, index) => {
    // 从数组中按索引获取容器
    const chartContainer = publisherChartRefs.value[index];
    
    // 检查容器是否存在
    if (!chartContainer) {
      console.warn(`发行商${index}图表容器不存在，当前索引对应的容器为:`, chartContainer);
      return;
    }

    // 检查游戏数据
    if (!publisher.top_games || publisher.top_games.length === 0) {
      console.warn(`发行商${index}（${publisher.publisher}）没有游戏数据`);
      return;
    }

    // 初始化图表
    const chart = echarts.init(chartContainer);
    chart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} 百万 ({d}%)' },
      legend: { orient: 'vertical', top: 'middle', right: 10, fontSize: 11 },
      series: [{
        name: '游戏销量',
        type: 'pie',
        radius: ['45%', '75%'],
        center: ['35%', '50%'],
        itemStyle: { borderRadius: 3, borderColor: '#fff', borderWidth: 1 },
        label: { show: true, fontSize: 11, formatter: '{b}: {d}%' },
        data: publisher.top_games.map(game => ({ name: game.name, value: game.sales }))
      }]
    });

    window.addEventListener('resize', () => chart.resize());
  });
};
</script>

<style scoped>
/* 样式保持不变，网格布局会自动适应10个项目 */
.analysis-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.page-title {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
  font-weight: 600;
}

.data-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 30px;
}

.card-title {
  color: #444;
  font-size: 18px;
  margin-top: 0;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f0f0f0;
}

.table-wrapper {
  overflow-x: auto;
}

.sales-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 600px;
}

.sales-table th,
.sales-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.sales-table th {
  background-color: #f5f7fa;
  font-weight: 600;
  color: #666;
}

.sales-table tr:hover {
  background-color: #f9f9f9;
}

.rank-cell {
  color: #f56c6c;
  font-weight: 600;
}

.name-cell {
  max-width: 250px;
}

.platform-cell {
  color: #1890ff;
}

.sales-cell {
  font-weight: 600;
}

.chart-container {
  width: 100%;
  height: 450px;
}

.publisher-cell {
  color: #722ed1;
}

.publishers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 10px;
}

.publisher-item {
  background: #f9f9f9;
  border-radius: 6px;
  padding: 15px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.publisher-title {
  font-size: 14px;
  color: #333;
  margin: 0 0 15px 0;
  padding-bottom: 5px;
  border-bottom: 1px dashed #eee;
}

.small-chart-container {
  width: 100%;
  height: 220px;
}

@media (max-width: 768px) {
  .chart-container {
    height: 300px;
  }

  .small-chart-container {
    height: 200px;
  }

  .publishers-grid {
    grid-template-columns: 1fr;
  }

  .data-card {
    padding: 15px;
  }
}
</style>
    