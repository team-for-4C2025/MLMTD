<template>
  <div id="app">
    <h2 class="title">实时流量</h2>
    <div class="container">
      <div ref="chartRef" class="chart"></div>
      <div id="infoContainer" class="info-container">
        <div class="legend">
          <span class="legend-color normal"></span>
          <span>正常流量</span>
        </div>
        <div class="legend">
          <span class="legend-color malicious"></span>
          <span>恶意流量</span>
        </div>
        <div class="slider-value">时间单位:</div>
        <div class="slider-container">
          <div class="slider-item" :class="{ 'active-slider-item': sliderValue === 0 }" @click="handleSliderChange(0)">
            min
          </div>
          <div class="slider-item" :class="{ 'active-slider-item': sliderValue === 1 }" @click="handleSliderChange(1)">
            hour
          </div>
          <div class="slider-item" :class="{ 'active-slider-item': sliderValue === 2 }" @click="handleSliderChange(2)">
            day
          </div>
        </div>
        <!-- <div class="slider-value"><span v-if="isBarChart">类型: 柱状图</span>
          <span v-else>类型: 折线图</span></div> -->
        <div class="toggle-container">
          <input type="checkbox" id="chart-toggle" v-model="isBarChart" @change="toggleChartType">
          <label for="chart-toggle"></label>
          <span class="toggle-label" :class="{ 'left': isBarChart, 'right':!isBarChart }">
            <span v-if="isBarChart">柱状图</span>
            <span v-else>折线图</span>
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import * as echarts from 'echarts';
import axios from 'axios';

const chartRef = ref<HTMLElement | null>(null);
const uploadTraffic = ref(0);
const downloadTraffic = ref(0);
let chartInstance: echarts.ECharts | null = null;
const sliderValue = ref(0); 
const isBarChart = ref(true); 

const getDtypeValue = () => {
  switch (sliderValue.value) {
    case 0:
      return "min";
    case 1:
      return "hour";
    case 2:
      return "day";
    default:
      return "min";
  }
};

const fetchData = async () => {
  try {
    const dtype = getDtypeValue();
    const response = await axios.post('http://localhost:8000/history', { dtype }, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    const data = response.data;

    const normalData = [];
    const attackData = [];
    for (let i = 1; i <= 7; i++) {
      normalData.push(data[`${i}n`]);
      attackData.push(data[`${i}a`]);
    }

    uploadTraffic.value = 0;
    downloadTraffic.value = 0;

    if (chartInstance) {
      const option = {
        xAxis: {
          type: 'category',
          data: ['1', '2', '3', '4', '5', '6', '7']
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '正常流量',
            type: isBarChart.value? 'bar' : 'line',
            data: normalData,
            itemStyle: {
              color: '#00CC00'
            },
            lineStyle: isBarChart.value? undefined : {
              color: '#00CC00'
            }
          },
          {
            name: '恶意流量',
            type: isBarChart.value? 'bar' : 'line',
            data: attackData,
            itemStyle: {
              color: '#FF0000'
            },
            lineStyle: isBarChart.value? undefined : {
              color: '#FF0000'
            }
          }
        ],
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow',
            shadowStyle: {
              color: 'rgba(0, 0, 0, 0.2)' 
            }
          },
          backgroundColor: '#ccc',
          padding: 10
        }
      };

      chartInstance.setOption(option);

      chartInstance.off('click');
      chartInstance.on('click', function (params) {
        const x = parseInt(params.name, 10);
        axios.post('http://localhost:8000/history_attack_distribution', { dtype: x }, {
          headers: {
            'Content-Type': 'application/json'
          }
        })
      });
    }
  } catch (error) {
    console.error('获取数据时出错:', error);
  }
};

const handleSliderChange = (value: number) => {
  sliderValue.value = value;
  fetchData();
};

const toggleChartType = () => {
  fetchData();
};

onMounted(() => {
  if (chartRef.value) {
    chartInstance = echarts.init(chartRef.value);
    const initialOption = {
      xAxis: {
        type: 'category',
        data: ['1', '2', '3', '4', '5', '6', '7']
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '正常流量',
          type: 'bar',
          data: Array.from({ length: 7 }, () => 0),
          itemStyle: {
            color: '#00CC00'
          }
        },
        {
          name: '恶意流量',
          type: 'bar',
          data: Array.from({ length: 7 }, () => 0),
          itemStyle: {
            color: '#FF0000'
          }
        }
      ],
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow',
          shadowStyle: {
            color: 'rgba(0, 0, 0, 0.2)' 
          }
        },
        backgroundColor: '#ccc',
        padding: 10
      }
    };

    chartInstance.setOption(initialOption);
    // 初始加载数据
    fetchData();
  }
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
  color: #333;
  font-size: 30px;
  margin:0;
  /* margin-bottom: 40px; */
  text-align: center;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
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

.slider-value {
  color: #333;
  font-size: 18px;
  margin-bottom: 0px;
  text-align: left;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
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

.slider-container {
  display: flex;
  width: 100%;
  flex-direction: column;
  justify-content: space-around;
  margin-top: 10px;
}

.slider-item {
  flex: 1;
  padding: 5px 0;
  text-align: center;
  border: 1px solid #ccc;
  cursor: pointer;
}

.active-slider-item {
  background-color: #ccc;
}

.toggle-container {
  position: relative;
  width: 100%;
  margin-top: 10px;
}

#chart-toggle {
  display: none;
}

#chart-toggle + label {
  display: block;
  position: relative;
  width: 60px;
  height: 30px;
  background-color: #ccc;
  border-radius: 15px;
  cursor: pointer;
  transition: background-color 0.3s;
}

#chart-toggle + label::after {
  content: '';
  position: absolute;
  top: 3px;
  left: 3px;
  width: 24px;
  height: 24px;
  background-color: white;
  border-radius: 50%;
  transition: left 0.3s;
}

#chart-toggle:checked + label {
  background-color: #00CC00;
}

#chart-toggle:checked + label::after {
  left: 33px;
}

.toggle-label {
  position: absolute;
  top: 50%;
  left: 70px;
  transform: translateY(-50%);
  white-space: nowrap;
}

.toggle-label.left {
  opacity: 1;
}

.toggle-label.right {
  opacity: 0;
}

#chart-toggle:checked ~ .toggle-label.left {
  opacity: 0;
}

#chart-toggle:checked ~ .toggle-label.right {
  opacity: 1;
}
</style>