<template>
  <div id="app">
    <h2 class="title">实时流量</h2>
    <div class="container">
      <div ref="chartRef" class="chart"></div>
      <div id="infoContainer" class="info-container">
        <div class="traffic-info">
          <span class="arrow up-arrow">↑</span>
          <span> 上行流量: <span id="uploadTraffic">{{ uploadTraffic }} Bps</span></span>
        </div>
        <div class="traffic-info">
          <span class="arrow down-arrow">↓</span>
          <span> 下行流量: <span id="downloadTraffic">{{ downloadTraffic }} Bps</span></span>
        </div>
        <div class="legend">
          <span class="legend-color normal"></span>
          <span>正常流量</span>
        </div>
        <div class="legend">
          <span class="legend-color malicious"></span>
          <span>恶意流量</span>
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
const uploadTraffic = ref(0);
const downloadTraffic = ref(0);
let chartInstance: echarts.ECharts | null = null;
let intervalId: number | null = null;

const fetchData = async () => {
  try {
    const response = await axios.get('http://localhost:8000/nrate');
    const normalRate = response.data.nrate;
    const attackRate = 100 - normalRate;
    uploadTraffic.value = response.data.upload_traffic;
    downloadTraffic.value = response.data.download_traffic;

    if (chartInstance) {
      const option = {
        series: [
          {
            type: 'pie',
            radius: ['50%', '70%'],
            avoidLabelOverlap: false,
            label: {
              show: true,
              position: 'center',
              formatter: `攻击率: ${attackRate}%`,
              color: 'black',
              fontSize: 20
            },
            labelLine: {
              show: false
            },
            data: [
              {
                value: attackRate,
                name: '攻击率',
                itemStyle: { color: '#FF0000' }
              },
              {
                value: normalRate,
                name: '正常率',
                itemStyle: { color: '#00CC00' }
              }
            ]
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
    if (!intervalId) {
      intervalId = setInterval(fetchData, 1000);
    }
  } else {
    if (intervalId) {
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
    intervalId = setInterval(fetchData, 1000);
    document.addEventListener('visibilitychange', handleVisibilityChange);
  }
});

onUnmounted(() => {
  if (intervalId) {
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
  gap: 20px;
  align-items: left;
}

.traffic-info {
  display: flex;
  align-items: center;
}

.arrow {
  font-size: 24px;
  margin-right: 10px;
}

.up-arrow {
  color: #0099FF;
}

.down-arrow {
  color: #FF9900;
}

.legend {
  display: flex;
  align-items: center;
}

.legend-color {
  display: inline-block;
  width: 10px;
  height: 10px;
  margin-right: 10px;
}

.normal {
  background-color: #00CC00;
}

.malicious {
  background-color: #FF0000;
}
</style>    