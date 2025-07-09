<template>
    <v-container>
      <v-row>
        <v-col
          v-for="equipment in equipmentList"
          :key="equipment.id"
          cols="12" sm="6" md="4"
        >
          <v-card class="mx-auto" outlined @click="goToEquipment(equipment.id)" hover>
            <v-card-title class="text-h6">{{ equipment.name }}</v-card-title>
            <v-card-subtitle>メーカー: {{ equipment.manufacturer }}</v-card-subtitle>
            <v-card-text>
              IP: {{ equipment.ip }}<br>
              ポート: {{ equipment.port }}
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </template>
  
  <script setup>
  import { useRouter } from 'vue-router'
  
  const router = useRouter()
  
  const equipmentList = [
    { id: 'eq001', name: 'A装置', manufacturer: 'Mitsubishi', ip: '192.168.0.101', port: 5000 },
    { id: 'eq002', name: 'B装置', manufacturer: 'Omron', ip: '192.168.0.102', port: 9600 },
    { id: 'eq003', name: 'C装置', manufacturer: 'Keyence', ip: '192.168.0.103', port: 8501 },
  ]
  
  const goToEquipment = (id) => {
    router.push(`/equipment/${id}`)
  }
  </script>
  