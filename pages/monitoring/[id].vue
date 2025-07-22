<template>
  <v-container fluid>
    <!-- ヘッダー部分 -->
    <v-row class="mb-4">
      <v-col cols="12">
        <v-card color="primary" dark class="pa-4">
          <v-row align="center">
            <v-col>
              <v-card-title class="text-h4">
                <v-icon large class="mr-3">mdi-monitor-dashboard</v-icon>
                {{ equipmentInfo?.equipment_id || 'N/A' }} - リアルタイムモニタリング
              </v-card-title>
              <v-card-subtitle>
                {{ equipmentInfo?.manufacturer }} {{ equipmentInfo?.series }}
                <v-chip 
                  :color="connectionStatus ? 'success' : 'error'" 
                  text-color="white" 
                  size="small" 
                  class="ml-2"
                >
                  {{ connectionStatus ? '接続中' : '切断' }}
                </v-chip>
              </v-card-subtitle>
            </v-col>
            <v-col cols="auto">
              <v-btn @click="goBack" variant="outlined" color="white">
                <v-icon left>mdi-arrow-left</v-icon>
                戻る
              </v-btn>
            </v-col>
          </v-row>
        </v-card>
      </v-col>
    </v-row>

    <!-- ステータスカード -->
    <v-row class="mb-4">
      <v-col cols="12" sm="6" md="2" v-for="(item, key) in monitoringData" :key="key">
        <v-card :color="getCardColor(item.status)" class="text-center pa-3" dark>
          <v-icon size="40" class="mb-2">{{ item.icon }}</v-icon>
          <div class="text-h4 font-weight-bold">{{ item.value || 'N/A' }}</div>
          <div class="text-subtitle-1">{{ item.label }}</div>
          <div class="text-caption">{{ item.unit }}</div>
          <v-chip 
            size="x-small" 
            :color="item.status === 'normal' ? 'success' : 'error'"
            class="mt-1"
          >
            {{ item.status === 'normal' ? '正常' : '異常' }}
          </v-chip>
        </v-card>
      </v-col>
    </v-row>

    <!-- アラート表示 -->
    <v-row v-if="alerts.length > 0" class="mb-4">
      <v-col cols="12">
        <v-alert
          v-for="alert in alerts"
          :key="alert.id"
          :type="alert.type"
          prominent
          border="start"
          :icon="alert.icon"
          closable
          @click:close="removeAlert(alert.id)"
        >
          <v-alert-title>{{ alert.title }}</v-alert-title>
          {{ alert.message }}
          <template v-slot:append>
            <div class="text-caption">{{ alert.timestamp }}</div>
          </template>
        </v-alert>
      </v-col>
    </v-row>

    <!-- リアルタイムグラフ -->
    <v-row>
      <v-col cols="12" md="6" v-for="chart in chartConfigs" :key="chart.id">
        <v-card class="pa-4" elevation="3">
          <v-card-title class="text-h6">
            <v-icon class="mr-2">{{ chart.icon }}</v-icon>
            {{ chart.title }}
          </v-card-title>
          <div style="height: 300px;">
            <Chart
              v-if="chart.data && chart.data.datasets[0].data.length > 0"
              :data="chart.data"
              :options="chart.options"
              type="line"
            />
            <div v-else class="d-flex align-center justify-center" style="height: 100%;">
              <div class="text-center text-grey">
                <v-icon size="48" color="grey">mdi-chart-line</v-icon>
                <div class="mt-2">データ待機中...</div>
              </div>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- 最新データログ -->
    <v-row class="mt-4">
      <v-col cols="12">
        <v-card class="pa-4" elevation="3">
          <v-card-title class="text-h6">
            <v-icon class="mr-2">mdi-table</v-icon>
            最新データ履歴（最新{{ dataHistory.length }}件）
          </v-card-title>
          <v-data-table
            :headers="tableHeaders"
            :items="dataHistory"
            density="compact"
            :items-per-page="10"
            class="mt-3"
          >
            <template #[`item.timestamp`]="{ item }">
              {{ formatDateTime(item.timestamp) }}
            </template>
            <template #[`item.error_code`]="{ item }">
              <v-chip
                size="small"
                :color="item.error_code ? 'error' : 'success'"
                text-color="white"
              >
                {{ item.error_code || '正常' }}
              </v-chip>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
} from 'chart.js'
import { Chart } from 'vue-chartjs'
import { ref, onMounted, onBeforeUnmount, reactive, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement
)

const route = useRoute()
const router = useRouter()
const { $socket } = useNuxtApp()

// データ定義
const equipmentId = route.params.id
const equipmentInfo = ref(null)
const connectionStatus = ref(false)
const dataHistory = ref([])
const alerts = ref([])

// モニタリングデータ
const monitoringData = reactive({
  production_count: {
    label: '生産数量',
    value: null,
    unit: '個',
    icon: 'mdi-counter',
    status: 'normal'
  },
  current: {
    label: '電流',
    value: null,
    unit: 'A',
    icon: 'mdi-flash',
    status: 'normal'
  },
  temperature: {
    label: '温度',
    value: null,
    unit: '℃',
    icon: 'mdi-thermometer',
    status: 'normal'
  },
  pressure: {
    label: '圧力',
    value: null,
    unit: 'MPa',
    icon: 'mdi-gauge',
    status: 'normal'
  },
  cycle_time: {
    label: 'サイクルタイム',
    value: null,
    unit: 's',
    icon: 'mdi-timer-outline',
    status: 'normal'
  },
  error_code: {
    label: 'エラーコード',
    value: null,
    unit: '',
    icon: 'mdi-alert-circle-outline',
    status: 'normal'
  }
})

// グラフ設定
const chartConfigs = ref([
  {
    id: 'current',
    title: '電流値',
    icon: 'mdi-flash',
    data: null,
    options: null
  },
  {
    id: 'temperature',
    title: '温度',
    icon: 'mdi-thermometer',
    data: null,
    options: null
  },
  {
    id: 'pressure',
    title: '圧力',
    icon: 'mdi-gauge',
    data: null,
    options: null
  },
  {
    id: 'cycle_time',
    title: 'サイクルタイム',
    icon: 'mdi-timer-outline',
    data: null,
    options: null
  }
])

// テーブルヘッダー
const tableHeaders = [
  { title: '時刻', value: 'timestamp', width: '180' },
  { title: '生産数量', value: 'production_count', align: 'center' },
  { title: '電流(A)', value: 'current', align: 'center' },
  { title: '温度(℃)', value: 'temperature', align: 'center' },
  { title: '圧力(MPa)', value: 'pressure', align: 'center' },
  { title: 'サイクルタイム(s)', value: 'cycle_time', align: 'center' },
  { title: 'エラーコード', value: 'error_code', align: 'center' }
]

// メソッド
const getCardColor = (status) => {
  switch (status) {
    case 'error': return 'error'
    case 'warning': return 'warning'
    default: return 'primary'
  }
}

const formatDateTime = (timestamp) => {
  return new Date(timestamp).toLocaleString('ja-JP')
}

const goBack = () => {
  router.push('/')
}

const removeAlert = (alertId) => {
  const index = alerts.value.findIndex(alert => alert.id === alertId)
  if (index !== -1) {
    alerts.value.splice(index, 1)
  }
}

const addAlert = (type, title, message) => {
  const alert = {
    id: Date.now(),
    type,
    title,
    message,
    timestamp: new Date().toLocaleString('ja-JP'),
    icon: type === 'error' ? 'mdi-alert-circle' : 'mdi-information'
  }
  alerts.value.unshift(alert)
  
  // 最大10件のアラートを保持
  if (alerts.value.length > 10) {
    alerts.value = alerts.value.slice(0, 10)
  }
}

const initializeCharts = () => {
  chartConfigs.value.forEach(chart => {
    chart.data = {
      labels: [],
      datasets: [{
        label: chart.title,
        data: [],
        borderColor: chart.id === 'current' ? '#2196F3' : 
                     chart.id === 'temperature' ? '#FF5722' :
                     chart.id === 'pressure' ? '#4CAF50' : '#FF9800',
        backgroundColor: 'transparent',
        tension: 0.4,
        pointRadius: 3,
        pointHoverRadius: 5
      }]
    }
    
    chart.options = {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 500 },
      scales: {
        x: {
          title: { display: true, text: '時刻' },
          type: 'category'
        },
        y: {
          title: { 
            display: true, 
            text: monitoringData[chart.id]?.unit || ''
          }
        }
      },
      plugins: {
        legend: { display: false },
        title: { display: false }
      }
    }
  })
}

const updateChartData = (newData) => {
  const timestamp = new Date(newData.timestamp).toLocaleTimeString('ja-JP')
  
  chartConfigs.value.forEach(chart => {
    const value = newData[chart.id]
    if (value !== null && value !== undefined) {
      // データ追加
      chart.data.labels.push(timestamp)
      chart.data.datasets[0].data.push(value)
      
      // 最大50点まで保持
      if (chart.data.labels.length > 50) {
        chart.data.labels.shift()
        chart.data.datasets[0].data.shift()
      }
    }
  })
}

const updateMonitoringData = (data) => {
  Object.keys(monitoringData).forEach(key => {
    if (data[key] !== null && data[key] !== undefined) {
      monitoringData[key].value = data[key]
      
      // ステータス判定（例：エラーコードがある場合は異常）
      if (key === 'error_code') {
        monitoringData[key].status = data[key] ? 'error' : 'normal'
      } else {
        monitoringData[key].status = 'normal'
      }
    }
  })
}

const fetchEquipmentInfo = async () => {
  try {
    const response = await fetch(`http://localhost:5000/api/equipment/${equipmentId}`)
    if (response.ok) {
      equipmentInfo.value = await response.json()
    }
  } catch (error) {
    console.error('設備情報取得エラー:', error)
  }
}

const fetchLatestData = async () => {
  try {
    const response = await fetch(`http://localhost:5000/api/logs/${equipmentId}/latest`)
    if (response.ok) {
      const data = await response.json()
      updateMonitoringData(data)
      updateChartData(data)
      dataHistory.value.unshift(data)
      if (dataHistory.value.length > 100) {
        dataHistory.value = dataHistory.value.slice(0, 100)
      }
    }
  } catch (error) {
    console.error('最新データ取得エラー:', error)
  }
}

// WebSocket接続設定
const setupWebSocket = () => {
  // Socket.IOクライアントが利用可能かチェック
  if (!$socket) {
    console.warn('Socket.IO client not available')
    return
  }
  
  $socket.connect()
  
  $socket.on('connect', () => {
    connectionStatus.value = true
    console.log('✅ WebSocket接続完了')
    
    // モニタリングルームに参加
    $socket.emit('join_monitoring', { equipment_id: equipmentId })
    console.log(`🏠 モニタリングルーム参加: equipment_${equipmentId}`)
  })
  
  $socket.on('disconnect', () => {
    connectionStatus.value = false
    console.log('❌ WebSocket切断')
  })
  
  // リアルタイムデータ受信
  $socket.on('plc_data_update', (data) => {
    if (data.equipment_id === equipmentId) {
      console.log('🔄 PLCデータ受信 (plc_data_update):', data)
      updateMonitoringData(data)
      updateChartData(data)
      
      // データ履歴に追加
      dataHistory.value.unshift(data)
      if (dataHistory.value.length > 100) {
        dataHistory.value = dataHistory.value.slice(0, 100)
      }
      
      // エラーアラート
      if (data.error_code) {
        addAlert('error', 'エラー発生', `エラーコード: ${data.error_code}`)
      }
    }
  })
  
  // 設備固有データ受信
  $socket.on('equipment_data_update', (data) => {
    if (data.equipment_id === equipmentId) {
      console.log('🔄 設備データ受信 (equipment_data_update):', data)
      updateMonitoringData(data)
      updateChartData(data)
      
      dataHistory.value.unshift(data)
      if (dataHistory.value.length > 100) {
        dataHistory.value = dataHistory.value.slice(0, 100)
      }
    }
  })
}

// ライフサイクル
onMounted(async () => {
  await fetchEquipmentInfo()
  await fetchLatestData()
  initializeCharts()
  setupWebSocket()
})

onBeforeUnmount(() => {
  if ($socket) {
    $socket.emit('leave_monitoring', { equipment_id: equipmentId })
    $socket.disconnect()
  }
})
</script>

<style scoped>
.text-h4 {
  font-weight: 600;
}

.v-card {
  transition: all 0.3s ease;
}

.v-card:hover {
  transform: translateY(-2px);
}
</style> 