<template>
  <div id="app">
    <h2 class="title">攻击分类</h2>
    <div class="container">
      <div ref="chartRef" class="chart"></div>
      <div id="infoContainer" class="info-container absolute right-0 bottom-0">
        <div v-for="(item, index) in dataLabels" :key="index" class="flex mb-2 text-left">
          <span class="color-dot w-10 h-10 rounded" :style="{ backgroundColor: colors[index] }"></span>
          <span class="ml-2 text-black">{{ item }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, onUnmounted } from 'vue';
import * as echarts from 'echarts';
import axios from 'axios';

const chartRef = ref<HTMLElement | null>(null);
const dataLabels = ref<string[]>([]);
const dataValues = ref<number[]>([]);
const colors = ref([
  '#FF5733', '#C70039', '#900C3F', '#581845', '#FFC300', '#DAF7A6',
  '#FFEB3B', '#FF9800', '#FF5722', '#795548', '#607D8B', '#009688',
  '#03A9F4', '#2196F3'
]);
let chartInstance: echarts.ECharts | null = null; // 用于存储 ECharts 实例
let intervalId: number | null = null;

const fetchData = async () => {
  try {
    const response = await axios.get('http://localhost:8000/atype');
    const data = response.data;
    dataLabels.value = Object.keys(data);
    dataValues.value = Object.values(data);

    if (chartInstance) {
      const option = {
        color: colors.value,
        series: [
          {
            type: 'pie',
            radius: ['0%', '70%'],
            avoidLabelOverlap: false,
            labelLine: {
              show: false
            },
            data: dataLabels.value.map((label, index) => ({
              value: dataValues.value[index],
              name: label
            }))
          }
        ]
      };

      chartInstance.setOption(option);
    }
  } catch (error) {
    console.error('Error fetching data:', error);
  }
};

const handleVisibilityChange = () => {
  if (document.visibilityState === 'visible') {
    if (intervalId === null) {
      intervalId = setInterval(fetchData, 1000); // 调整轮询时间间隔
    }
  } else {
    if (intervalId!== null) {
      clearInterval(intervalId);
      intervalId = null;
    }
  }
};

onMounted(() => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value);
    const initialOption = {
      series: [
        {
          type: 'pie',
          radius: ['50%', '70%'],
          avoidLabelOverlap: false,
          label: {
            show: false,
            position: 'center'
          },
          labelLine: {
            show: false
          },
          data: [
            { value: 100, name: 'background', itemStyle: { color: 'gray' } }
          ]
        }
      ]
    };

    chartInstance.setOption(initialOption);
    fetchData();
    intervalId = setInterval(fetchData, 1000); // 调整轮询时间间隔
    document.addEventListener('visibilitychange', handleVisibilityChange);
  }
});

onUnmounted(() => {
  if (intervalId!== null) {
    clearInterval(intervalId);
  }
  document.removeEventListener('visibilitychange', handleVisibilityChange);
});
</script>

<style scoped>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  /* margin-top: 60px; */
}

.title {
  color: #333; /* 标题颜色 */
  font-size: 30px; /* 标题字体大小 */
  /* margin-bottom: 40px; */
  margin:0;
  text-align: center;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2); /* 文字阴影效果 */
}

.container {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: top;
  gap: 20px;
  max-width: 600px;
  max-height: 300px;
  margin: 0 auto;
}

.chart {
  min-width: 300px;
  height: 300px;
}

.info-container {
  max-width: 200px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
  align-items: flex-start;
}

.color-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  margin-right: 10px;
}

.text-black {
  color: black;
}

.text-left {
  text-align: left;
}
</style>
