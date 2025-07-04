<template>
  <div class="blackip-container">
    <div v-for="(ip, index) in blackIpSet" :key="index" class="ip-container">
      <div class="text-container">
        <span class="ip-text">{{ ip }}</span>
      </div>
      <button @click="deleteblackIP(ip)" class="delete-button">删除</button>
    </div>
    <button @click="toggleAdding" class="add-button">添加</button>
    <div v-if="isAdding" class="add-ip-container">
      <input v-model="newIP" type="text" placeholder="输入 IP 地址" class="ip-input">
      <button @click="addblackIP" class="add-small-button">添加</button>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue';
import axios from 'axios';

interface ModifyIP {
  ip: string;
  op_type: boolean; // true 表示添加，false 表示删除
}

// 使用 Set 类型
const blackIpSet = ref(new Set<string>());
const newIP = ref('');
const isAdding = ref(false);

const fetchblackIP = async () => {
  try {
    const response = await axios.get('http://localhost:8000/black_ip');
    // 将后端返回的数组转换为 Set
    blackIpSet.value = new Set(response.data);
  } catch (error) {
    console.error('获取黑名单 IP 出错:', error);
  }
};

const addblackIP = async () => {
  const ip = newIP.value;
  if (ip) {
    const req: ModifyIP = {
      ip,
      op_type: true
    };
    try {
      const response = await axios.post('http://localhost:8000/black_ip', req);
      if (response.data) {
        blackIpSet.value.add(ip);
        newIP.value = '';
        isAdding.value = false;
      }
    } catch (error) {
      console.error('添加黑名单 IP 出错:', error);
    }
  }
};

const deleteblackIP = async (ip: string) => {
  const req: ModifyIP = {
    ip,
    op_type: false
  };
  try {
    const response = await axios.post('http://localhost:8000/blackip', req);
    if (response.data) {
      blackIpSet.value.delete(ip);
    }
  } catch (error) {
    console.error('删除黑名单 IP 出错:', error);
  }
};

const toggleAdding = () => {
  isAdding.value =!isAdding.value;
};

onMounted(() => {
  fetchblackIP();
});
</script>

<style scoped>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

.blackip-container {
  width: 400px;
  margin: 0 auto;
}

.ip-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border: 1px solid #e0e0e0;
  border-radius: 5px;
  margin-bottom: 10px;
}

.text-container {
  flex: 1;
}

.ip-text {
  flex: 1;
}

.delete-button {
  background-color: #ff5733;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 3px;
  cursor: pointer;
}

.add-button {
  background-color: #3399ff;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 3px;
  cursor: pointer;
  width: 100%;
  margin-top: 10px;
}

.add-ip-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.ip-input {
  flex: 1;
  padding: 5px;
  border: 1px solid #e0e0e0;
  border-radius: 3px;
}

.add-small-button {
  background-color: #3399ff;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 3px;
  cursor: pointer;
}
</style>    