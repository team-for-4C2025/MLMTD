<template>
  <el-container class="app-container">
    <el-header class="top-bar">
      <h1 class="page-title">恶意流量检测平台</h1>
    </el-header>
    <el-container class="content-container">
      <el-aside width="250px" class="sidebar">
        <div class="logo">流量监测选项:</div>
        <el-menu
          class="sidebar-menu"
          :default-active="currentComponent"
          background-color="#304156"
          text-color="#fff"
          active-text-color="#409EFF"
        >
          <el-menu-item index="RealTimeTrafficAnalysisUI" @click="selectUI('RealTimeTrafficAnalysisUI')">
            <el-icon><Monitor /></el-icon>
            <span>实时监控</span>
          </el-menu-item>
          <el-menu-item index="HistoryTrafficAnalysisUI" @click="selectUI('HistoryTrafficAnalysisUI')">
            <el-icon><DataAnalysis /></el-icon>
            <span>历史数据</span>
          </el-menu-item>
          <el-menu-item index="PcapFileAnalysisUI" @click="selectUI('PcapFileAnalysisUI')">
            <el-icon><Document /></el-icon>
            <span>日志信息</span>
          </el-menu-item>
          <el-menu-item index="SettingUI" @click="selectUI('SettingUI')">
            <el-icon><Setting /></el-icon>
            <span>系统设置</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main class="ui-container">
        <div class="header-wrapper">
          <div class="page-header">
            <el-icon class="back-icon"><House /></el-icon>
            <span class="page-title">{{ uiName }}</span>
          </div>
        </div>
        <div class="ui">
          <component :is="resolvedComponent" />
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<script lang="ts" setup>
import { ref, defineAsyncComponent } from 'vue';
import { Monitor, DataAnalysis, Document, Setting, House } from '@element-plus/icons-vue';

// 动态加载各个 UI 组件
const RealTimeTrafficAnalysisUI = defineAsyncComponent(() => import('./views/RealTimeTrafficAnalysisUI.vue'));
const HistoryTrafficAnalysisUI = defineAsyncComponent(() => import('./views/HistoryTrafficAnalysisUI.vue'));
const PcapFileAnalysisUI = defineAsyncComponent(() => import('./views/PcapFileAnalysisUI.vue'));
const SettingUI = defineAsyncComponent(() => import('./views/SettingUI.vue'));

const currentComponent = ref('RealTimeTrafficAnalysisUI');
// 定义一个 ref 来存储实际要渲染的组件
const resolvedComponent = ref(RealTimeTrafficAnalysisUI);
// 定义一个 string 来存储当前 UI 的名称
const uiName = ref('实时流量分析');

// 定义一个方法用于选择 UI 组件
const selectUI = (componentName: string) => {
  currentComponent.value = componentName;
  switch (componentName) {
    case 'RealTimeTrafficAnalysisUI':
      resolvedComponent.value = RealTimeTrafficAnalysisUI;
      uiName.value = '实时流量分析';
      break;
    case 'HistoryTrafficAnalysisUI':
      resolvedComponent.value = HistoryTrafficAnalysisUI;
      uiName.value = '历史流量分析';
      break;
    case 'PcapFileAnalysisUI':
      resolvedComponent.value = PcapFileAnalysisUI;
      uiName.value = 'PCAP 文件分析';
      break;
    case 'SettingUI':
      resolvedComponent.value = SettingUI;
      uiName.value = '设置';
      break;
    default:
      break;
  }
};
</script>

<style scoped>
/* 全局样式重置 */
body {
  margin: 0;
  padding: 0;
}

.app-container {
  height: 100vh;
  width: 100vw;
}

/* top-bar 样式 */
.top-bar {
  background: linear-gradient(90deg, #409EFF, #79bbff);
  color: white;
  padding: 0;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  height: 60px !important;
  position: relative;
  z-index: 1000;
}

.top-bar .page-title {
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

/* content-container 样式 */
.content-container {
  height: calc(100vh - 60px);
}

/* sidebar 样式 */
.sidebar {
  background-color: #304156;
  color: #fff;
  border-right: 1px solid #263445;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  padding: 0;
  width: 250px !important;
}

.logo {
  padding: 20px 0;
  text-align: center;
  font-size: 18px;
  font-weight: 600;
  color: #E5EAF3;
  background-color: #263445;
  height: 60px;
  line-height: 60px;
  letter-spacing: 0.5px;
  position: relative;
  overflow: hidden;
}

.logo::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 40%;
  height: 2px;
  background-color: #409EFF;
  border-radius: 2px;
}

.sidebar-menu {
  border-right: none;
}

.sidebar-menu .el-menu-item.is-active {
  position: relative;
  overflow: hidden;
}

.sidebar-menu .el-menu-item.is-active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 4px;
  height: 100%;
  background-color: #409EFF;
}

/* ui-container 样式 */
.ui-container {
  padding: 20px;
  background-color: #f5f7fa;
}

.header-wrapper {
  position: relative;
  width: 100%;
  margin-bottom: 20px;
}

.page-header {
  display: flex;
  align-items: center;
  height: 40px;
  background-color: #fff;
  padding: 0 12px;
  border-bottom: 1px solid #e4e7ed;
  border-radius: 4px 4px 0 0;
}

.back-icon {
  font-size: 18px;
  margin-right: 8px;
  color: #606266;
}

.page-header .page-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

/* 删除旧的横线样式 */
.horizontal-bar {
  display: none;
}

.ui {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  min-height: calc(100vh - 180px);
}

/* 修复Element Plus的图标显示 */
.el-icon {
  margin-right: 8px;
}
</style>