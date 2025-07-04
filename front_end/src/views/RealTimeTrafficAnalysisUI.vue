<template>
  <div class="real-time-analysis">
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>实时流量监控</span>
            </div>
          </template>
          <RealTimeTraffic />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>恶意流量分类</span>
            </div>
          </template>
          <MacliousTrafficClassification />
        </el-card>
      </el-col>
    </el-row>
    
    <el-card shadow="hover" class="traffic-analysis-card">
      <template #header>
        <div class="card-header with-tag">
          <span>流量分析</span>
          <!-- <el-tag type="success" effect="dark">使用模型: {{ modelName || '加载中...' }}</el-tag> -->
        </div>
      </template>
      
      <div ref="ipcontainer" class="ip-container">
        <el-empty v-if="!hasData && !errorMessage" description="暂无数据"></el-empty>
        <el-alert v-if="errorMessage" :title="errorMessage" type="error" :closable="false"></el-alert>
        <!-- IP列表将通过JavaScript动态添加 -->
      </div>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import RealTimeTraffic from '../components/RealTimeTrafficGraph.vue';
import MacliousTrafficClassification from '../components/MacliousTrafficClassificationGraph.vue';
import { onMounted, onUnmounted, ref, computed } from 'vue';

const ipcontainer = ref<HTMLElement | null>(null);
let intervalId: number | null = null;
let modelIntervalId: number | null = null;
const errorMessage = ref<string>('');
const modelName = ref<string>('');
const ipData = ref<Record<string, number>>({});

// 计算属性判断是否有数据
const hasData = computed(() => Object.keys(ipData.value).length > 0);

// 定义 ipdict 的类型
type IpDict = Record<string, number>;

const fetchData = async () => {
  try {
    const response = await fetch('http://127.0.0.1:8000/maliciousrate');
    if (!response.ok) {
      throw new Error('网络响应不正常');
    }
    const ipdict: IpDict = await response.json();
    ipData.value = ipdict;
    console.log('从后端获取的数据:', ipdict);

    if (ipcontainer.value) {
      // 清空之前的 IP 列表
      ipcontainer.value.innerHTML = '';

      // 遍历 ipdict 并创建对应的卡片
      for (const ipKey in ipdict) {
        const attackRate = ipdict[ipKey];
        
        // 创建元素
        const ipCard = document.createElement('div');
        ipCard.className = 'ip-card';
        
        // 设置攻击率百分比
        const percentValue = Math.round(attackRate * 100);
        
        // 根据攻击率决定标签类型
        let tagType = 'success';
        if (percentValue > 30) tagType = 'warning';
        if (percentValue > 70) tagType = 'danger';

        // 构建卡片内容
        ipCard.innerHTML = `
          <div class="ip-info">
            <div class="ip-address">IP: ${ipKey}</div>
            <div class="ip-tag el-tag el-tag--${tagType} el-tag--dark">
              攻击率: ${percentValue}%
            </div>
          </div>
          <div class="progress-container">
            <div class="progress-bar" style="width: ${percentValue}%; background-color: ${getColor(attackRate)}"></div>
          </div>
        `;
        
        ipcontainer.value.appendChild(ipCard);
      }
    }
    errorMessage.value = '';
  } catch (error) {
    console.error('获取数据时出错:', error);
    errorMessage.value = '获取数据时出错，请稍后重试。';
  }
};

const fetchModel = async () => {
  try {
    const response = await fetch('http://127.0.0.1:8000/model');
    if (!response.ok) {
      throw new Error('网络响应不正常');
    }
    const model = await response.text();
    modelName.value = model;
  } catch (error) {
    console.error('获取模型名称时出错:', error);
  }
};

onMounted(() => {
  // 初始加载数据
  fetchData();
  fetchModel();

  // 每 1 秒轮询一次获取 IP 数据
  intervalId = setInterval(fetchData, 1000);
  // 每 1 秒轮询一次获取模型名称
  modelIntervalId = setInterval(fetchModel, 1000);
});

onUnmounted(() => {
  // 组件卸载时清除定时器
  if (intervalId) {
    clearInterval(intervalId);
  }
  if (modelIntervalId) {
    clearInterval(modelIntervalId);
  }
});

// 根据攻击率计算颜色的函数
function getColor(rate: number) {
  // 0 到 0.1 之间的线性映射，从绿色到红色
  const green = Math.round(255 * (1 - rate * 10));
  const red = Math.round(255 * (rate * 10));
  return `rgb(${red}, ${green}, 0)`;
}
</script>

<style scoped>
.real-time-analysis {
  width: 100%;
}

.chart-row {
  margin-bottom: 20px;
}

.chart-card {
  height: 600px;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  font-weight: 600;
  font-size: 15px;
  color: #303133;
  position: relative;
  padding: 0 6px;
}

.card-header::before {
  content: '';
  position: absolute;
  left: -4px;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 14px;
  background-color: #409EFF;
  border-radius: 2px;
}

.card-header.with-tag {
  margin-bottom: 0;
}

.el-card {
  transition: all 0.3s;
  border: none;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.08) !important;
}

.el-card:hover {
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.12) !important;
}

.traffic-analysis-card {
  margin-bottom: 20px;
}

.ip-container {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  padding: 10px 0;
  min-height: 200px;
}

.ip-card {
  width: calc(50% - 15px);
  padding: 12px;
  border-radius: 6px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  background-color: #fff;
  transition: all 0.3s;
  border: 1px solid #ebeef5;
}

.ip-card:hover {
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.ip-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.ip-address {
  font-weight: bold;
  font-size: 14px;
}

.progress-container {
  height: 8px;
  background-color: #ebeef5;
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease, background-color 0.5s ease;
}

/* 调整按钮尺寸 */
.el-button {
  padding: 8px 15px;
  font-size: 13px;
}
</style>