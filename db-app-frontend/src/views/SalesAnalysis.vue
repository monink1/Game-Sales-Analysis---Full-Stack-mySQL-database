<template>
  <div class="container">
    <h1>游戏销量数据分析平台</h1>

    <!-- 1. 各地区Top20游戏组合图 -->
    <div class="chart-card">
      <h2>各地区最畅销20款游戏（折线+柱状组合图）</h2>
      <div ref="regionTop20Chart" class="chart-wrapper"></div>
    </div>

    <!-- 2. 各类型最畅销游戏柱状图 -->
    <div class="chart-card">
      <h2>各游戏类型最畅销游戏销量（从小到大排序）</h2>
      <div ref="genreTopChart" class="chart-wrapper"></div>
    </div>

    <!-- 3. 三条件筛选器及结果展示（已删除封面图列） -->
    <div class="filter-section">
      <h2>游戏筛选器（Genre + Platform + Publisher）</h2>
      <div class="filter-controls">
        <div class="filter-item">
          <label>选择类型：</label>
          <select v-model="selectedGenre" @change="handleFilterChange">
            <option value="">-- 请选择 --</option>
            <option v-for="genre in allGenres" :key="genre">{{ genre }}</option>
          </select>
        </div>
        <div class="filter-item">
          <label>选择平台：</label>
          <select v-model="selectedPlatform" @change="handleFilterChange">
            <option value="">-- 请选择 --</option>
            <option v-for="platform in allPlatforms" :key="platform">{{ platform }}</option>
          </select>
        </div>
        <div class="filter-item">
          <label>选择发行商：</label>
          <select v-model="selectedPublisher" @change="handleFilterChange">
            <option value="">-- 请选择 --</option>
            <option v-for="publisher in allPublishers" :key="publisher">{{ publisher }}</option>
          </select>
        </div>
        <button 
          class="query-btn" 
          @click="fetchFilteredGames" 
          :disabled="!isFilterComplete"
        >
          查询符合条件的游戏
        </button>
      </div>

      <!-- 筛选结果表格（无封面图列） -->
      <div v-if="filteredGames.length > 0" class="result-table">
        <h3>筛选结果（共 {{ filteredGames.length }} 款）</h3>
        <table>
          <thead>
            <tr>
              <th>排名</th>
              <th>游戏名称</th>
              <th>类型</th>
              <th>平台</th>
              <th>发行商</th>
              <th>全球销量（百万）</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(game, index) in filteredGames" :key="index + game.name">
              <td>{{ index + 1 }}</td>
              <td>{{ game.name || game.Name || '未知游戏' }}</td>
              <td>{{ game.genre || game.Genre || '未知类型' }}</td>
              <td>{{ game.platform || game.Platform || '未知平台' }}</td>
              <td>{{ game.publisher || game.Publisher || '未知发行商' }}</td>
              <td>{{ (Number(game.global_sales || game.Global_Sales) || 0).toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else-if="isFilterComplete && filteredGames.length === 0" class="no-result">
        没有找到符合条件的游戏，请重新选择筛选条件
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import axios from 'axios';
import * as echarts from 'echarts';

// 图表容器
const regionTop20Chart = ref(null);
const genreTopChart = ref(null);

// 数据存储
const regionGames = ref([]);
const genreGames = ref([]);
const allGenres = ref([]);
const allPlatforms = ref([]);
const allPublishers = ref([]);
const selectedGenre = ref('');
const selectedPlatform = ref('');
const selectedPublisher = ref('');
const filteredGames = ref([]);

// 筛选条件是否完整
const isFilterComplete = () => {
  return !!selectedGenre.value && !!selectedPlatform.value && !!selectedPublisher.value;
};

// 初始化所有数据
const initAllData = async () => {
  try {
    const [regionRes, genreRes, filterRes] = await Promise.all([
      axios.get('http://localhost:5000/api/sales/by-region-top20?n=20'),
      axios.get('http://localhost:5000/api/sales/by-genre-top'),
      axios.get('http://localhost:5000/api/filters/meta')
    ]);

    regionGames.value = (regionRes.data.data || []).map(game => ({
      name: game.name || game.Name || '未知游戏',
      publisher: game.publisher || game.Publisher || '未知发行商',
      platform: game.platform || game.Platform || '未知平台',
      year: game.year || game.Year || '未知年份',
      na_sales: Number(game.na_sales || game.NA_Sales) || 0,
      eu_sales: Number(game.eu_sales || game.EU_Sales) || 0,
      jp_sales: Number(game.jp_sales || game.JP_Sales) || 0,
      other_sales: Number(game.other_sales || game.Other_Sales) || 0,
      global_sales: Number(game.global_sales || game.Global_Sales) || 0
    }));

    genreGames.value = (genreRes.data.data || []).map(item => ({
      genre: item.genre || item.Genre || '未知类型',
      game_name: item.game_name || item.top_game_name || item.Name || '未知游戏',
      sales: Number(item.sales || item.Global_Sales) || 0
    }));

    allGenres.value = filterRes.data.genres || [];
    allPlatforms.value = filterRes.data.platforms || [];
    allPublishers.value = filterRes.data.publishers || [];
  } catch (err) {
    console.error('数据初始化失败：', err);
    alert('数据加载失败，请检查后端服务');
  }
};

// 查询筛选结果
const fetchFilteredGames = async () => {
  if (!isFilterComplete()) return;
  try {
    const res = await axios.get('http://localhost:5000/api/games/filtered', {
      params: { genre: selectedGenre.value, platform: selectedPlatform.value, publisher: selectedPublisher.value }
    });
    filteredGames.value = (res.data.data || []).map(game => ({
      name: game.name || game.Name || '未知游戏',
      genre: game.genre || game.Genre || '未知类型',
      platform: game.platform || game.Platform || '未知平台',
      publisher: game.publisher || game.Publisher || '未知发行商',
      global_sales: game.global_sales || game.Global_Sales || 0
    }));
  } catch (err) {
    console.error('筛选查询失败：', err);
    alert('查询失败，请重试');
  }
};

// 筛选条件变化时清空结果
const handleFilterChange = () => {
  filteredGames.value = [];
};

// 初始化地区Top20图表
const initRegionChart = () => {
  if (!regionTop20Chart.value || regionGames.value.length === 0) return;
  const chart = echarts.init(regionTop20Chart.value);
  const regionConfig = [
    { key: 'na_sales', name: '北美', color: '#409eff' },
    { key: 'eu_sales', name: '欧洲', color: '#67c23a' },
    { key: 'jp_sales', name: '日本', color: '#f56c6c' },
    { key: 'other_sales', name: '其他地区', color: '#909399' }
  ];

  const series = [];
  regionConfig.forEach(region => {
    const sortedGames = [...regionGames.value]
      .sort((a, b) => b[region.key] - a[region.key])
      .slice(0, 20);

    series.push({
      name: `${region.name}销量`,
      type: 'bar',
      data: sortedGames.map(game => ({
        value: game[region.key],
        gameInfo: { name: game.name, platform: game.platform, publisher: game.publisher, year: game.year, sales: game[region.key] }
      })),
      itemStyle: { color: region.color },
      barWidth: '30%'
    });

    series.push({
      name: `${region.name}趋势`,
      type: 'line',
      data: sortedGames.map(game => game[region.key]),
      symbol: 'circle',
      lineStyle: { color: region.color },
      itemStyle: { color: region.color }
    });
  });

  chart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        const barParam = params.find(p => p.seriesType === 'bar');
        const gameInfo = barParam?.data?.gameInfo || {};
        const sales = Number(gameInfo.sales) || 0;
        return `
          <div style="display:flex;gap:10px;padding:8px;">
            <div>
              <div style="font-weight:bold;">${gameInfo.name || '未知游戏'}</div>
              <div>发行商：${gameInfo.publisher || '未知'}</div>
              <div>平台：${gameInfo.platform || '未知'}</div>
              <div>年份：${gameInfo.year || '未知'}</div>
              <div style="color:#409eff;">销量：${sales.toFixed(2)} 百万</div>
            </div>
          </div>
        `;
      },
      confine: true
    },
    legend: { data: regionConfig.map(r => r.name), bottom: 0, left: 'center' },
    grid: { left: '5%', right: '5%', bottom: '15%', top: '10%', containLabel: true },
    xAxis: { type: 'category', data: Array.from({ length: 20 }, (_, i) => `Top${i+1}`) },
    yAxis: { type: 'value', name: '销量（百万）', min: 0 },
    series: series
  });

  window.addEventListener('resize', () => chart.resize());
};

// 初始化类型畅销榜图表
const initGenreChart = () => {
  if (!genreTopChart.value || genreGames.value.length === 0) return;
  const chart = echarts.init(genreTopChart.value);
  const sortedData = [...genreGames.value].sort((a, b) => a.sales - b.sales);

  chart.setOption({
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const data = params[0].data || {};
        return `
          <div>类型：${data.genre || '未知'}</div>
          <div>游戏：${data.game_name || '未知'}</div>
          <div>销量：${Number(data.sales || 0).toFixed(2)} 百万</div>
        `;
      }
    },
    grid: { left: '12%', right: '8%', bottom: '10%', top: '10%' },
    xAxis: { type: 'value', name: '销量（百万）' },
    yAxis: { type: 'category', data: sortedData.map(item => item.genre) },
    series: [{
      type: 'bar',
      data: sortedData.map(item => ({ value: item.sales, genre: item.genre, game_name: item.game_name })),
      itemStyle: { color: '#67c23a' },
      label: { show: true, position: 'right' }
    }]
  });

  window.addEventListener('resize', () => chart.resize());
};

// 页面加载初始化
onMounted(async () => {
  await initAllData();
  await nextTick();
  setTimeout(() => {
    initRegionChart();
    initGenreChart();
  }, 500);
});
</script>

<style scoped>
.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', sans-serif;
}

h1 {
  text-align: center;
  color: #333;
  margin: 20px 0 40px;
}

.chart-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
  padding: 20px;
  margin-bottom: 30px;
}

.chart-wrapper {
  width: 100%;
  height: 500px;
  margin-top: 15px;
}

.filter-section {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
  padding: 20px;
}

.filter-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin: 20px 0;
  align-items: center;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 180px;
}

.query-btn {
  padding: 8px 20px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-left: auto;
}

.query-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.result-table {
  margin-top: 20px;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

th, td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background: #f5f7fa;
  font-weight: 600;
}

.no-result {
  margin: 20px 0;
  color: #666;
  padding: 10px;
  text-align: center;
}

@media (max-width: 768px) {
  .filter-controls {
    flex-direction: column;
    align-items: stretch;
  }
  .query-btn {
    margin-left: 0;
  }
  .chart-wrapper {
    height: 350px;
  }
}
</style>
