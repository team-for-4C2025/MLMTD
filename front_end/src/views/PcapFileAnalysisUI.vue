<template>
  <div class="pcap-analysis">
    <el-card shadow="hover" class="pcap-form-card">
      <template #header>
        <div class="card-header">
          <span>PCAP文件分析</span>
        </div>
      </template>
      
      <el-form @submit.prevent="submitPath" label-position="top">
        <el-form-item label="请输入PCAP文件夹路径">
          <el-input 
            v-model="path" 
            placeholder="请输入PCAP文件夹路径"
            clearable>
            <template #append>
              <el-button type="primary" @click="submitPath" :loading="isLoading">
                提交
              </el-button>
            </template>
          </el-input>
        </el-form-item>
      </el-form>
      
      <div v-if="showSavedPath" class="save-path-info">
        <el-alert
          title="分析完成"
          type="success"
          description="结果已保存"
          show-icon
          :closable="false">
          <template #default>
            <p>保存路径: <el-tag type="info">{{ store_path }}</el-tag></p>
          </template>
        </el-alert>
      </div>
    </el-card>
    
    <!-- 进度条 -->
    <el-dialog
      v-model="isLoading"
      title="文件处理中"
      width="30%"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false">
      <div class="progress-container">
        <el-progress 
          :percentage="progress" 
          :status="progress === 100 ? 'success' : ''"
          :stroke-width="20">
        </el-progress>
        <p class="progress-text">处理进度: {{ progress }}%</p>
        <el-alert
          v-if="errorMessage"
          :title="errorMessage"
          type="error"
          show-icon>
        </el-alert>
      </div>
    </el-dialog>
    
    <!-- 完成提示框 -->
    <el-dialog
      v-model="showModal"
      title="处理完成"
      width="30%">
      <span>{{ modalMessage }}</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="closeModal">
            确认
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import axios from 'axios'; // 引入axios用于获取PCAP分析保存地址

interface ModifyPathRequest {
  path: string;
}

const path = ref('');
const result = ref('');
const isError = ref(false);
const isLoading = ref(false); // 用于控制遮罩层和进度条的显示
const progress = ref(0); // 用于存储当前进度，初始化为 0
const errorMessage = ref(''); // 用于存储错误信息
let progressInterval: any; // 用于存储定时器
const store_path = ref(''); // 改为响应式，用于存储PCAP分析保存地址
const showSavedPath = ref(false); // 控制保存路径的展示
const showModal = ref(false); // 控制提示框的显示
const modalMessage = ref(''); // 提示框的消息内容

// 获取PCAP分析保存地址的函数
const getResPath = async () => {
  try {
    const response = await axios.get('http://localhost:8000/respath');
    store_path.value = response.data;
  } catch (error) {
    console.error('获取PCAP分析保存地址时出错:', error);
  }
};

const submitPath = async () => {
  await getResPath(); // 在提交前先获取保存地址
  
  if (!path.value) {
    errorMessage.value = '请输入有效的文件路径';
    return;
  }
  
  isLoading.value = true;
  progress.value = 0;
  errorMessage.value = '';
  clearInterval(progressInterval); // 确保清除之前的定时器

  const requestData: ModifyPathRequest = {
    path: path.value
  };
  try {
    const response = await fetch('http://127.0.0.1:8000/pcap_process', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData)
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    result.value = JSON.stringify(data);
    console.log('请求处理成功:', data);
    isError.value = false;

    // 开始定时检查进度
    progressInterval = setInterval(async () => {
      try {
        const progressResponse = await fetch('http://127.0.0.1:8000/process');
        if (!progressResponse.ok) {
          throw new Error(`HTTP error! status: ${progressResponse.status}`);
        }
        const progressData = await progressResponse.json();
        console.log('获取进度:', progressData);
        if (progressData >= 0) {
          progress.value = progressData;
          if (progressData === 100) {
            clearInterval(progressInterval);
            isLoading.value = false;
            showSavedPath.value = true;
            modalMessage.value = `结果已经保存到文件 ${store_path.value} 中`; // 使用响应式的store_path
            showModal.value = true;
          }
        }
      } catch (error) {
        errorMessage.value = `获取进度出错: ${(error as Error).message}`;
        console.error('获取进度出错:', (error as Error).message);
        clearInterval(progressInterval);
        isLoading.value = false;
      }
    }, 10); // 每0.1秒请求一次进度

  } catch (error) {
    result.value = `请求出错: ${(error as Error).message}`;
    isError.value = true;
    errorMessage.value = `请求处理出错: ${(error as Error).message}`;
    isLoading.value = false;
  }
};

const closeModal = () => {
  showModal.value = false;
};
</script>

<style scoped>
.pcap-analysis {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.pcap-form-card {
  width: 80%;
  max-width: 700px;
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

.progress-container {
  padding: 20px 0;
}

.progress-text {
  text-align: center;
  margin-top: 15px;
  font-size: 14px;
  color: #606266;
}

.save-path-info {
  margin-top: 20px;
}

/* 调整按钮尺寸 */
.el-button {
  padding: 8px 15px;
  font-size: 13px;
}
</style>