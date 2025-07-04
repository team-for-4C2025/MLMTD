<template>
  <div class="settings-page">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card shadow="hover" class="ip-management-card">
          <template #header>
            <div class="card-header">
              <span>IP 管理</span>
            </div>
          </template>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-button 
                type="primary" 
                @click="showWhiteIP = true; showBlackIP = false; showOverlay = true" 
                :class="{ 'is-active': showWhiteIP }"
                plain>
                <el-icon><Check /></el-icon>
                管理白名单
              </el-button>
            </el-col>
            <el-col :span="12">
              <el-button 
                type="danger" 
                @click="showBlackIP = true; showWhiteIP = false; showOverlay = true" 
                :class="{ 'is-active': showBlackIP }"
                plain>
                <el-icon><CircleClose /></el-icon>
                管理黑名单
              </el-button>
            </el-col>
          </el-row>
        </el-card>
        
        <el-card shadow="hover" class="settings-card">
          <template #header>
            <div class="card-header">
              <span>系统设置</span>
            </div>
          </template>
          
          <el-form label-width="180px" class="settings-form">
            <el-form-item label="监听端口">
              <el-input-number v-model="port" :min="1" :max="65535" disabled class="setting-input"></el-input-number>
              <el-button type="primary" size="small" @click="openModifyOverlay('port')" class="edit-button">
                <el-icon><Edit /></el-icon>修改
              </el-button>
            </el-form-item>
            
            <el-form-item label="特征提取间隔">
              <el-input-number v-model="delay" :min="0" disabled class="setting-input"></el-input-number>
              <el-button type="primary" size="small" @click="openModifyOverlay('delay')" class="edit-button">
                <el-icon><Edit /></el-icon>修改
              </el-button>
            </el-form-item>
            
            <el-form-item label="日志存储路径">
              <el-input v-model="logPath" disabled class="setting-input"></el-input>
              <el-button type="primary" size="small" @click="openModifyOverlay('logPath')" class="edit-button">
                <el-icon><Edit /></el-icon>修改
              </el-button>
            </el-form-item>
            
            <el-form-item label="PCAP分析保存地址">
              <el-input v-model="resPath" disabled class="setting-input"></el-input>
              <el-button type="primary" size="small" @click="openModifyOverlay('resPath')" class="edit-button">
                <el-icon><Edit /></el-icon>修改
              </el-button>
            </el-form-item>
            
            <el-form-item label="黑名单阈值 (%)">
              <el-slider
                v-model="blackThreshold"
                :min="0"
                :max="100"
                :format-tooltip="formatTooltip"
                disabled
                class="setting-slider">
              </el-slider>
              <el-button type="primary" size="small" @click="openModifyOverlay('blackThreshold')" class="edit-button">
                <el-icon><Edit /></el-icon>修改
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- IP管理对话框 -->
    <el-dialog
      v-model="showOverlay"
      :title="showWhiteIP ? '白名单管理' : '黑名单管理'"
      width="60%"
      destroy-on-close>
      <WhiteIP v-if="showWhiteIP" @hideOverlay="hideOverlay" />
      <BlackIP v-if="showBlackIP" @hideOverlay="hideOverlay" />
    </el-dialog>
    
    <!-- 修改值对话框 -->
    <el-dialog
      v-model="showModifyOverlay"
      :title="getModifyTitle()"
      width="30%">
      <el-form>
        <el-form-item :label="getModifyLabel()">
          <el-input v-model="newValue" v-if="!isNumberType()"></el-input>
          <el-input-number v-model="numericValue" v-else :min="getMinValue()" :max="getMaxValue()"></el-input-number>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="closeModifyOverlay">取消</el-button>
          <el-button type="primary" @click="submitModify">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 错误提示对话框 -->
    <el-dialog
      v-model="showErrorOverlay"
      title="错误"
      width="30%">
      <el-alert
        title="修改失败，请重试！"
        type="error"
        :closable="false"
        show-icon>
      </el-alert>
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="closeErrorOverlay">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { Check, CircleClose, Edit } from '@element-plus/icons-vue';
import WhiteIP from '../components/WhiteIP.vue';
import BlackIP from '../components/BlackIP.vue';

const showWhiteIP = ref(false);
const showBlackIP = ref(false);
const showOverlay = ref(false);
const showModifyOverlay = ref(false);
const showErrorOverlay = ref(false);
const newValue = ref('');
const numericValue = ref(0);
const modifyType = ref('');
const port = ref<number>(0);
const delay = ref<number>(0);
const logPath = ref('');
const resPath = ref('');
const blackThreshold = ref<number>(0);

const hideOverlay = () => {
  showWhiteIP.value = false;
  showBlackIP.value = false;
  showOverlay.value = false;
};

const formatTooltip = (val: number) => {
  return val + '%';
};

const isNumberType = () => {
  return ['port', 'delay', 'blackThreshold'].includes(modifyType.value);
};

const getMinValue = () => {
  switch (modifyType.value) {
    case 'port': return 1;
    case 'delay': return 0;
    case 'blackThreshold': return 0;
    default: return 0;
  }
};

const getMaxValue = () => {
  switch (modifyType.value) {
    case 'port': return 65535;
    case 'blackThreshold': return 100;
    default: return Number.MAX_SAFE_INTEGER;
  }
};

const getModifyTitle = () => {
  switch (modifyType.value) {
    case 'port': return '修改监听端口';
    case 'delay': return '修改特征提取间隔';
    case 'logPath': return '修改日志路径';
    case 'resPath': return '修改PCAP分析保存地址';
    case 'blackThreshold': return '修改黑名单阈值';
    default: return '修改设置';
  }
};

const getModifyLabel = () => {
  switch (modifyType.value) {
    case 'port': return '端口';
    case 'delay': return '特征提取间隔';
    case 'logPath': return '日志路径';
    case 'resPath': return 'PCAP分析保存地址';
    case 'blackThreshold': return '阈值(%)';
    default: return '值';
  }
};

const openModifyOverlay = (type: string) => {
  showModifyOverlay.value = true;
  modifyType.value = type;
  switch (type) {
    case 'port':
      newValue.value = port.value.toString();
      numericValue.value = port.value;
      break;
    case 'delay':
      newValue.value = delay.value.toString();
      numericValue.value = delay.value;
      break;
    case 'logPath':
      newValue.value = logPath.value;
      break;
    case 'resPath':
      newValue.value = resPath.value;
      break;
    case 'blackThreshold':
      newValue.value = blackThreshold.value.toString();
      numericValue.value = blackThreshold.value;
      break;
  }
};

const closeModifyOverlay = () => {
  showModifyOverlay.value = false;
  newValue.value = '';
};

const submitModify = async () => {
  let url = '';
  let data = {};
  
  // 如果是数字类型，使用numericValue
  const value = isNumberType() ? numericValue.value : newValue.value;
  
  switch (modifyType.value) {
    case 'port':
      url = 'http://localhost:8000/port';
      data = { port: value };
      break;
    case 'delay':
      url = 'http://localhost:8000/delay';
      data = { delay: value };
      break;
    case 'logPath':
      url = 'http://localhost:8000/logpath';
      data = { path: value };
      break;
    case 'resPath':
      url = 'http://localhost:8000/respath';
      data = { path: value };
      break;
    case 'blackThreshold':
      url = 'http://localhost:8000/black_threshold';
      data = { threshold: value };
      break;
  }
  try {
    const response = await axios.post(url, data);
    if (response.data) {
      switch (modifyType.value) {
        case 'port':
          port.value = isNumberType() ? numericValue.value : parseInt(newValue.value);
          break;
        case 'delay':
          delay.value = isNumberType() ? numericValue.value : parseInt(newValue.value);
          break;
        case 'logPath':
          logPath.value = newValue.value;
          break;
        case 'resPath':
          resPath.value = newValue.value;
          break;
        case 'blackThreshold':
          blackThreshold.value = isNumberType() ? numericValue.value : parseFloat(newValue.value);
          break;
      }
      closeModifyOverlay();
    } else {
      showErrorOverlay.value = true;
    }
  } catch (error) {
    showErrorOverlay.value = true;
  }
};
onMounted(async () => {
  try {
    const portResponse = await axios.get('http://localhost:8000/port');
    port.value =parseInt(portResponse.data);

    const delayResponse = await axios.get('http://localhost:8000/delay');
    delay.value = parseInt(delayResponse.data);

    const logPathResponse = await axios.get('http://localhost:8000/logpath');
    logPath.value = logPathResponse.data;

    const resPathResponse = await axios.get('http://localhost:8000/respath');
    resPath.value = resPathResponse.data;

    const blackThresholdResponse = await axios.get('http://localhost:8000/black_threshold');
    blackThreshold.value = parseInt(blackThresholdResponse.data);
  } catch (error) {
    console.error('获取初始值时出错:', error);
  }
});

const closeErrorOverlay = () => {
  showErrorOverlay.value = false;
};
</script>

<style scoped>
.settings-page {
  width: 100%;
}

.ip-management-card {
  margin-bottom: 20px;
}

.settings-card {
  margin-bottom: 20px;
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

.is-active {
  font-weight: bold;
}

.settings-form {
  margin-top: 20px;
}

.setting-input {
  width: 300px;
}

.setting-slider {
  width: 300px;
  display: flex;
  align-items: center;
  /* margin-right: 20px; */
}

.edit-button {
  margin-left: 10px;
  padding: 6px 12px;
  font-size: 12px;
}

.active-dropdown {
  font-weight: bold;
  color: #409EFF;
}

/* 调整按钮尺寸 */
.el-button {
  padding: 8px 15px;
  font-size: 13px;
}
</style>